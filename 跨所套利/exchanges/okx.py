import ccxt
import pandas as pd


class Okx(ccxt.okx):

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
        # instruments okx 需要pos *精度
        # print(dir(self))
        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.privateGetAccountPositions({'instType': 'SWAP'})['data'], dtype=float)  # 获取合约仓位
        # 获取精度
        df_size = pd.DataFrame(self.publicGetPublicInstruments({'instType': 'SWAP'})['data'], dtype=float)  # 获取合约仓位
        df = pd.merge(df, df_size, on='instId', how='left')
        df.rename(columns={'instId': 'symbol', 'markPx': 'markPrice', 'pos': 'positionAmt'}, inplace=True)
        # usdt合约面值统一
        df.loc[df['ccy'] == 'USDT', 'positionAmt'] = df['positionAmt'] * df['ctVal']
        df['positionValue'] = df['positionAmt'] * df['markPrice']

        # usd 合约单独处理
        df.loc[df['ctValCcy'] == 'USD', 'positionValue'] = df['positionAmt'] * df['ctVal']
        df.loc[df['ctValCcy'] == 'USD', 'positionAmt'] = df['positionValue'] / df['markPrice']
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df = df[['exchange', 'account', 'symbol', 'markPrice', 'positionAmt', 'positionValue']]
        df = df[df['positionAmt'] != 0]
        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('-SWAP', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('-USDT-SWAP', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('-USD-SWAP', ''))

        return df

    def fetch_swap_asset(self):
        asset = self.privateGetAccountBalance()['data'][0]['totalEq']

        # assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        # assett3.to_json('okx-AR.json')

        return float(asset)
