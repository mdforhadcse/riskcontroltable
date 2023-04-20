import ccxt
import pandas as pd
class Coinex(ccxt.coinex):
    def fetch_swap_postion(self):
        """
        获取币安合约持仓数据
        :return:
        """

        # ==========获取合约账户信息==========

        df = pd.DataFrame(self.perpetualPrivateGetPositionPending()['data'],dtype=float)
        mark_price = self.perpetualPublicGetMarketTickerAll()['data']['ticker']
        mark_list = list()
        for item in mark_price.items():


            key = item[0]
            value = item[1]
            value.update({'market':key})
            mark_list.append(value)
            #print(value)
        df_price = pd.DataFrame(mark_list,dtype=float)
        df = pd.merge(left=df,right=df_price,on='market',how='inner')
        df.loc[df['side'] == 1,'amount'] = -df['amount']

        df.rename(columns={'market': 'symbol', 'sign_price': 'markPrice', 'amount': 'positionAmt'}, inplace=True)
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df = df[['exchange', 'account', 'symbol', 'markPrice', 'positionAmt']]

        df['positionValue'] = df['markPrice']*df['positionAmt']

        df['symbol_pair'] = df['symbol']
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('USDT', '-USDT'))
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace, args=('BUSD', '-BUSD'))

        df['symbol'] = df['symbol'].apply(str.replace, args=('USDT', ''))
        df['symbol'] = df['symbol'].apply(str.replace, args=('BUSD', ''))
        return df

    def fetch_swap_asset(self):
        #print(self.__dir__())

        asset = pd.DataFrame(self.perpetualPrivateGetAssetQuery()['data'], dtype=float)  # 获取合约仓位
        margin = float(asset.loc['margin','USDT'])
        available = float(asset.loc['available','USDT'])
        profit_unreal = float(asset.loc['profit_unreal','USDT'])

        # assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        # assett3.to_json('coinex-AR.json')

        return margin+available+profit_unreal