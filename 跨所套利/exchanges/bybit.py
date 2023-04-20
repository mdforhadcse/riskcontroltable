import ccxt
import pandas as pd
from tabulate import tabulate


class Bybit(ccxt.bybit):
    def fetch_swap_postion(self):
        """
        获取币安合约持仓数据
        :return:
        """
        #
        # ==========获取合约账户信息==========

        df = pd.DataFrame(self.private_get_private_linear_position_list()["result"], dtype=float)  # 获取合约仓位
        list_ = list(df['data'])
        df = pd.DataFrame(list_, dtype=float)
        # 获取标记价格
        df_price = pd.DataFrame(self.publicGetV2PublicTickers()['result'],
                                dtype=float)  # 获取合约仓位 self.publicGetV2PublicTickers()['result']
        # print(df_price)
        df = pd.merge(df, df_price, on='symbol', how='inner')

        df.rename(columns={'future': 'symbol', 'mark_price': 'markPrice', 'liq_price': 'forcePrice'}, inplace=True)
        df['positionAmt'] = -df['free_qty']
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df['positionValue'] = df['positionAmt'] * df['markPrice']
        df = df[['exchange', 'account', 'symbol', 'markPrice', 'positionAmt', 'positionValue', 'forcePrice']]
        df = df[df['positionAmt'] != 0]

        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USDT', '-USDT'))
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('BUSD', '-BUSD'))
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USD', 'USD'))

        df['symbol'] = df['symbol'].apply(str.replace, args=('USDT', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('BUSD', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('USD', ''))

        return df

    def fetch_swap_asset(self):
        # print(dir(self))
        asset = pd.DataFrame(self.privateGetV2PrivateWalletBalance()['result'], dtype=float)  # 获取合约仓位

        # assett1 = pd.DataFrame(self.parse_funding_rate('1INCHUSDT'))  # 获取合约仓位
        # print(assett1)
        # assett2 = pd.DataFrame(self.fetch_funding_rate('1INCHUSDT')['info'])  # 获取合约仓位
        # assett3 = pd.DataFrame(self.fetch_funding_rate('1INCHUSDT')['info']['result'])  # 获取合约仓位
        assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        assett3.to_json('bybit-AR.json')

        asset = asset.loc['equity', 'USDT']

        # dff = pd.DataFrame(self.fetch_markets())
        # print(dff)

        return float(asset)
