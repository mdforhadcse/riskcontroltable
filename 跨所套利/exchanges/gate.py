import ccxt
import pandas as pd
class Gate(ccxt.gateio):
    def fetch_swap_postion(self):
        """
        获取币安合约持仓数据
        :return:
        """

        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.privateFuturesGetSettlePositions({'settle':'usdt'}), dtype=float)  # 获取合约仓位
        df_size = pd.DataFrame(self.publicFuturesGetSettleContracts({'settle':'usdt'}), dtype=float)    #获取合约精度
        df_size.rename(columns={'name': 'contract'}, inplace=True)

        df = pd.merge(df, df_size, on='contract', how='left')
        df['positionAmt'] = df['quanto_multiplier'] * df['size']
        df.rename(columns={'contract': 'symbol', 'mark_price_x': 'markPrice'}, inplace=True)
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName

        df = df[['exchange','account', 'symbol', 'markPrice', 'positionAmt']]
        df['positionValue'] = df['positionAmt'] * df['markPrice']
        df = df[df['positionAmt'] != 0]
        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol'].apply(str.replace, args=('_USDT', '-USDT'))
        df['symbol'] = df['symbol'].apply(str.replace, args=('_USDT', ''))
        return df
    def fetch_swap_asset(self):
        #print(self.__dir__())
        data = self.privateFuturesGetSettleAccounts({'settle':'usdt'})
        unrealised_pnl = float(data['unrealised_pnl'])
        total = float(data['total'])
        asset = unrealised_pnl + total

        # assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        # assett3.to_json('gate-AR.json')

        return asset