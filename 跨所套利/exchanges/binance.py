import ccxt
import pandas as pd
from pprint import pprint


class Binance(ccxt.binance):
    binance_list = ['a', 'k']

    def fetch_swap_postion(self):
        """
        account         账户名
        symbol          交易对
        markPrice       标记价格
        positionAmt     仓位数量
        positionValue   仓位市值
        获取币安合约持仓数据
        :return:
        """
        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.fapiPrivateV2_get_account()["positions"], dtype=float)  # 获取合约仓位  # get Exchange position
        # df.to_csv('df.csv')
        df_price = pd.DataFrame(self.fapiPublicGetPremiumIndex(), dtype=float)  # Get Exchange price
        # df_price.to_excel()
        # self.options['defaultType'] = 'future'
        # pdd = pd.DataFrame(self.fetch_transaction_fee(self))
        # print(pdd)
        # pdd.to_csv('funding.csv')
        # df.to_csv('df2.csv')
        df = pd.merge(df, df_price, on='symbol', how='inner')  # marge df and df_price, make single dataframe
        # df.to_csv('df_merge.csv')

        df['exchange'] = self.__class__.__name__  # Exchange name
        df['account'] = self.accountName  # account Name
        df = df[['exchange', 'account', 'symbol', 'markPrice', 'positionAmt']]  # insert deleted value in df
        # print(df.to_markdown())
        df['positionValue'] = df['positionAmt'] * df['markPrice']  # calculate position Value
        # print(df.to_markdown())
        df = df[df['positionAmt'] != 0]  # insert only non zero value
        # print(df.to_markdown())
        df['symbol_pair'] = df['symbol']  # symbol pair
        # print(df.to_markdown())
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USDT', '-USDT'))  # only get USDT symbol pair
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('BUSD', '-BUSD'))  # only get BUSD symbol pair
        # print(df.to_markdown())
        # df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USD', '-USD'))

        df['symbol'] = df['symbol'].apply(str.replace, args=('USDT', ''))  # only get USDT symbol
        df['symbol'] = df['symbol'].apply(str.replace, args=('BUSD', ''))  # only get BUSD symbol
        # print(df.to_markdown())
        # df['symbol'] = df['symbol'].apply(str.replace, args=('USD', ''))
        # print(df)
        return df

    def fetch_swap_asset(self):
        asset = pd.DataFrame(self.fapiPrivateV2_get_account()['assets'], dtype=float)  # 获取合约仓位
        asset.to_csv('all_asset.csv')
        usdt = float(asset.loc[asset['asset'] == 'USDT', 'marginBalance'])  # get usdt balance
        busd = float(asset.loc[asset['asset'] == 'BUSD', 'marginBalance'])  # get busd balance

        # assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        # assett3.to_json('binance-AR.json')

        return usdt + busd  # total asset return
