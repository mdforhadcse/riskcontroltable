import ccxt
import pandas as pd


class Bitget(ccxt.bitget):
    def fetch_swap_postion(self):
        """
        获取币安合约持仓数据
        :return:
        """

        # ==========获取合约账户信息==========
        df = pd.DataFrame(self.privateMixGetPositionAllPosition({'productType': 'umcbl'})["data"],
                          dtype=float)  # 获取合约仓位 # get Exchange position
        df.loc[df['holdSide'] == 'short', 'total'] = -df['total']
        df_price = pd.DataFrame(self.publicMixGetMarketTickers({'productType': 'umcbl'})["data"],
                                dtype=float)  ## Get Exchange price
        df = pd.merge(df, df_price, on='symbol', how='inner')  # marge df and df_price, make single dataframe

        df.rename(columns={'last': 'markPrice', 'total': 'positionAmt'}, inplace=True)
        df['positionValue'] = df['markPrice'] * df['positionAmt']
        df['exchange'] = self.__class__.__name__
        df['account'] = self.accountName
        df = df[
            ['exchange', 'account', 'symbol', 'markPrice', 'positionAmt', 'positionValue']]  # insert deleted value in df
        df = df[df['positionAmt'] != 0]
        df['symbol_pair'] = df['symbol']  # get the symbol
        df['symbol_pair'] = df['symbol_pair'].apply(str.replace,
                                                    args=('USDT_UMCBL', '-USDT'))  # only get USDT_UMCBL symbol pair
        df['symbol'] = df['symbol'].apply(str.replace, args=('USDT_UMCBL', ''))
        return df

    def fetch_swap_asset(self):
        # print(self.__dir__())
        asset = self.privateMixGetAccountAccounts({'productType': 'umcbl'})['data'][0]['usdtEquity']
        # asset = pd.DataFrame(self.v2PrivateGetWalletBalance()['result'], dtype=float)  # 获取合约仓位

        # assett3 = pd.DataFrame(self.fetch_funding_rate('ARUSDT'))  # 获取合约仓位
        # assett3.to_json('bitget-AR.json')

        return float(asset)
