import requests
import unittest
import json
import math
from Interface.test_requests_pk import requests_packge
binance_last = 9409.31
r_huobi_last = 9409.96
r_ok_last = 9409.5

class test_mock_mi():

    def test_send_requestr(price_list):
        price_list=[]
        #binanceice_list
        binance=requests_packge("https://binance-api.deepcoin.pro/api/v3/ticker/price?symbol=BTCUSDT",requersts_type='get')
        r_binance = binance.getJson()
        n_price=r_binance.get('price')
        global binance_last
        if math.fabs(float(n_price)-float(binance_last)) / float(binance_last) > 0.25:
            return price_list.append(0)
        else:
            binance_last=n_price
            price_list.append(n_price)

        #huobi
        huobi = requests_packge("https://huobi-api.deepcoin.pro/market/trade?symbol=btcusdt",
                                  requersts_type='get')

        r_huobi = huobi.getJson()
        huobi_price=r_huobi.get('tick')['data'][0]['price']
        if math.fabs(huobi_price-r_huobi_last)/r_huobi_last>0.25:
            return price_list.append(0)
            print(r_huobi)
        else:
            huobi_price = r_huobi
            price_list.append(huobi_price)






        # ok
        #传地址
        ok = requests_packge("https://okex-api.deepcoin.pro/api/spot/v3/instruments/BTC-USDT/ticker",
                                  requersts_type='get')
        #取请求的返回值
        r_ok = ok.getJson()
        r_ok_price = r_ok.get('ask')
        if math.fabs(float(r_ok_price)-r_ok_last)/r_ok_last>0.25:
            return price_list.append(0)
            print(r_ok_price)
        else:
            price_list.append(huobi_price)

        print(r_ok)
        #保存进list
        price_list.append(r_ok.get('ask'))
        print(price_list)


        return price_list
