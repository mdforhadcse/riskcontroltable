from config import account_list, proxies
from exchanges import *
import ccxt
import pandas as pd
import time
import warnings
import schedule
from notify import notifier
from notify import Platform
import copy
from pprint import pprint

whiteListed = pd.read_csv('whiteListed.csv')

warnings.filterwarnings('ignore')  # warning will be ignored


def fetch_position():
    # 遍历所有账户
    accountsPosition = pd.DataFrame()  # declare a variable to store accountsPosition in the panda dataframe
    exchangesMassage = []  # a message list
    for account in copy.deepcopy(account_list):  # traverse deleted the exchanges using api that describe in
        exchange_class = account.pop('exchange')  # pop exchange info from account and store it exchange_class
        if proxies:  # checking for proxies
            account.update(
                {'proxies': {'http': 'http://localhost:7890', 'https': 'http://localhost:7890'}})  # update proxy url
        exchange = eval(exchange_class)(account)  # checking the expression between exchange_class and account
        # print(exchange)

        accountPosition = exchange.fetch_swap_postion()  # get the exchange position for every exchange from exchange

        # print(accountPosition)
        accountSwapAsset = exchange.fetch_swap_asset()  # get the total asset for every exchange from exchange class
        # print(accountSwapAsset)

        exchangeMassage = {'账户-account': f'{account["accountName"]}',  # account
                           '合约本金-ContractTotalAsset': accountSwapAsset,  # total asset
                           '多单市值-LongMarketCap': accountPosition.loc[
                               accountPosition['positionValue'] > 0, 'positionValue'].sum(),
                           '空单市值-ShortMarketValue': accountPosition.loc[
                               accountPosition['positionValue'] < 0, 'positionValue'].sum(),
                           '仓位总市值-TotalMarketValue': abs(  # The total market value of the position
                               accountPosition.loc[accountPosition['positionValue'] < 0, 'positionValue'].sum()) + abs(
                               accountPosition.loc[accountPosition['positionValue'] > 0, 'positionValue'].sum()),
                           '仓位净市值-NetMarketValue':
                               accountPosition.loc[
                                   accountPosition['positionValue'] < 0, 'positionValue'].sum() +  # net market value
                               accountPosition.loc[accountPosition['positionValue'] > 0, 'positionValue'].sum()
                           }

        exchangesMassage.append(exchangeMassage)  # update the exchangeMassage
        accountsPosition = accountsPosition.append(accountPosition)  # update the accountsPosition
        # print(accountsPosition)

    exchangesMassage = pd.DataFrame(exchangesMassage)  # make the exchangesMassage list into dataframe
    # pprint(accountsPosition)
    exchangesMassage['多单比例-Multi-SingleRatio'] = exchangesMassage['多单市值-LongMarketCap'] / exchangesMassage[
        '合约本金-ContractTotalAsset']  # multi-single ratio = long market value / total asset
    exchangesMassage['空单比例-EmptyOrderRatio'] = exchangesMassage['空单市值-ShortMarketValue'] / exchangesMassage[
        '合约本金-ContractTotalAsset']  # Empty order ratio =  short market value / total asset
    exchangesMassage['总市值比例-TotalMarketCapRatio'] = exchangesMassage['仓位总市值-TotalMarketValue'] / \
                                                         exchangesMassage[
                                                             '合约本金-ContractTotalAsset']  # Total market value ratio = total market value / total asset
    exchangesMassage['净市值比例-NetMarketCapRatio'] = exchangesMassage['仓位净市值-NetMarketValue'] / exchangesMassage[
        '合约本金-ContractTotalAsset']  # Net market value ratio = net market value / total asset

    symbolsPosition = pd.DataFrame()
    for symbol, group in accountsPosition.groupby('symbol'):  # sort/grouping data based on symbol
        group['数量对冲-VolumeHedge'] = group['positionAmt'].sum()  # volume hedging = total sum of positionAmt
        group['市值对冲-MarketCapHedge'] = group['positionValue'].sum()  # market cap hedge = total sum of positionValue
        symbolsPosition = symbolsPosition.append(group)  # append group in symbolsPosition

    # for updated whitelist symbol
    matchedWhiteList = pd.merge(symbolsPosition, whiteListed, on=["exchange", "account", "symbol"], how="outer",
                                indicator=True)
    matchedWhiteList = matchedWhiteList.loc[matchedWhiteList["_merge"] == "left_only"].drop("_merge", axis=1)
    print(matchedWhiteList)

    # matchedWhiteList = pd.DataFrame()
    # for i in range(len(whiteListed['account'].values)):
    #     df2 = symbolsPosition[(symbolsPosition.account == whiteListed['account'].values[i]) & (
    #             symbolsPosition.symbol == whiteListed['symbol'].values[i])]
    #     matchedWhiteList = matchedWhiteList.append(df2)  # get matched coined with whitelist from symbolsPosition

    SumPositionAmt = pd.DataFrame()
    SumPositionAmt['symbol'] = matchedWhiteList['symbol']
    SumPositionAmt['positionAmt'] = matchedWhiteList['positionAmt'].astype('float')

    MarketCapHedge = pd.DataFrame()
    MarketCapHedge['symbol'] = matchedWhiteList['symbol']
    MarketCapHedge['USDT'] = matchedWhiteList['市值对冲-MarketCapHedge']
    MarketCapHedge = MarketCapHedge.drop_duplicates()
    print(MarketCapHedge)

    positiveAndNegative = SumPositionAmt.positionAmt.lt(0).groupby(SumPositionAmt.symbol).transform('nunique').eq(2)
    SumPositionAmt = SumPositionAmt.loc[positiveAndNegative]  # there must be at least one positive and negative

    SumPositionAmt = SumPositionAmt[SumPositionAmt.duplicated(['symbol'], keep=False)]  # must be duplicated symbol
    # print(SumPositionAmt)

    # print(SumPositionAmt.to_markdown())
    # remove other column
    symbolPositionAmtSum = SumPositionAmt.groupby('symbol').sum()
    symbolPositionAmtSumMarketCapHedge = pd.merge(symbolPositionAmtSum, MarketCapHedge, on=["symbol"], how="outer", indicator=True)
    symbolPositionAmtSumMarketCapHedge = symbolPositionAmtSumMarketCapHedge.loc[symbolPositionAmtSumMarketCapHedge["_merge"] == "both"].drop("_merge", axis=1)


    today_day_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))  # get date time
    filepath = f'{today_day_time}-RiskControlTable.xlsx'  # generate file name based on date time
    with pd.ExcelWriter(filepath) as write:  # write information to excel
        exchangesMassage.to_excel(write, sheet_name=f'交易所数据-ExchangeData',
                                  index=False)
        accountsPosition.to_excel(write, sheet_name=f'仓位数据-交易所分类-Exchange',
                                  index=False)
        symbolsPosition.to_excel(write, sheet_name=f'仓位数据-币种分类-Symbol',
                                 index=False)
        # updatedSymbolsPosition.to_excel(write, sheet_name=f'仓位数据-币种分类-SymbolUpdate',
        #                          index=False)
        matchedWhiteList.to_excel(write, sheet_name=f'敞口检查exposure check',
                                  index=False)
        symbolPositionAmtSumMarketCapHedge.to_excel(write, sheet_name=f'敞口检查exposure check', startcol=12, startrow=0)

    notifier.notify("Position-持仓表", "持仓数据表", file_path=filepath,
                    platform=Platform.Mail)  # send Position table, Position Data Sheet via mail notification
    # notifier.notify("提醒机器人", "RiskControlTable 持仓表更新成功 \n查收请打开超弦公用邮箱\n chaoxian20220628@163.com",
    #                 platform=Platform.Dingtalk)  # Dingtalk bot notification
    # print(len(deleted))


if __name__ == '__main__':  # run deleted function

    filepath = "notify/notify.toml"
    notifier.set_platforms_with_file(filepath)
    fetch_position()

    schedule.every(5).hours.do(fetch_position)  # after every 30 it will execute

    while True:
        try:  # Exception handling
            schedule.run_pending()
            time.sleep(1)
        except Exception:
            notifier.notify("报错机器人", "RiskControlTable 持仓表更新错误\n 请联系福哈德", platform=Platform.Dingtalk)
            exit()
