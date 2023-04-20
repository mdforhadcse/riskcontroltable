import ccxt
import pandas as pd
class FTX(ccxt.ftx):



    def fetch_swap_postion(self):
        """
        获取币安合约持仓数据
        :return:
        """
        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.privateGetPositions()["result"], dtype=float)  # 获取合约仓位
        #格式统一
        df.rename(columns={'future': 'symbol', 'entryPrice': 'markPrice', 'netSize': 'positionAmt'}, inplace=True)
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df = df[['exchange','account', 'symbol', 'markPrice', 'positionAmt']]
        df['positionValue'] = df['positionAmt'] * df['markPrice']
        df = df[df['positionAmt'] != 0]

        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('-PERP', '-USDT'))
        df['symbol'] = df['symbol'].apply(str.replace,args=('-PERP',''))

        return df
    def fetch_swap_asset(self):
        #print(dir(self))
        asset = self.privateGetAccount()['result']['totalAccountValue']

        return float(asset)

