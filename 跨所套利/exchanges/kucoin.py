import ccxt
import pandas as pd


class Kucoin(ccxt.kucoin):

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
        # print(dir(self))
        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.futuresPrivateGetPositions()['data'], dtype=float)
        # markPrice currentQty currentCost
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df.rename(columns={'currentQty': 'positionAmt', 'currentCost': 'positionValue'}, inplace=True)
        df = df[['exchange', 'account', 'symbol', 'markPrice', 'positionAmt', 'positionValue']]
        df = df[df['positionAmt'] != 0]
        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USDTM', 'USDT'))
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('BUSDM', 'BUSD'))
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USD', '-USD'))

        df['symbol'] = df['symbol'].apply(str.replace, args=('USDTM', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('BUSDM', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('USD', ''))

        # print(dff)funding-history'

        return df

    def fetch_swap_asset(self):
        usdt = self.futuresPrivateGetAccountOverview({'currency': 'USDT'})['data']['marginBalance']
        return usdt
