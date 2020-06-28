import unittest

import ddt
import json
from Interface.test_login_denglu import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
import requests
from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.read_excel import read_excel

wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'限价买跌')
db_link=db_commit()
test = Test_Login('315702','315703')
token_test=test.test_log()
'''
限价买跌
'''
@ddt.ddt()
class Test_Login(unittest.TestCase):
    def setUp(self):
        LOG.info('限价买跌计算强平价开始')
    def tearDown(self):
        LOG.info('限价买跌计算强平价结束')

    @ddt.data(*excel.next())
    def test_shuj(self,data):
        '''
        计算强评价
        维持保证金
        注意：取参数时，需要查看execl是否有多余的空格
        :param data:
        :return:
        '''


        quantity=float(data['quantity(数量)'])
        lever=float(data['lever(杠杆)'])
        bs_flag=int(data['bs_flag(1买跌/2买涨)'])
        price=data['price(限价单)']
        order_type=int(data['order_type(订单类型1市场 2限价)'])
        contract_id=data['contract_id(交易对)']
        paramt_type=data['期望请求方式']
        print(lever)
        #1、市场价买涨算强平价格计算
        #2、多仓强平价格 = 开仓价格 * (1 - 起始保证金率 + 维持保证金率)
        #查询维持保证金率
        sql=('SELECT * FROM pc_risk_limit')
        maintenance_margin=db_link.get_one(sql)#查询维持保证金率第一条数据
        maintenance=float(maintenance_margin['maintenance_margin_rate'])#取出维持保证金率
        print('维持保证金',0.00500000)
        # #起始保证金率(1 - 1 / lever)
        Strong_parity=price*(1-1/lever+maintenance)
        print('强平价',Strong_parity)


        paramt={'quantity':quantity,'lever':lever,'bs_flag':bs_flag,'price':price,'order_type':order_type,'contract_id':contract_id,'price':price} #拼接参数
        print(paramt)
        for i in  token_test['token']:#循环里面token_test的值
            sql_usdt_Balance =requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance',requersts_type='get',paramt=paramt,headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print(i)

            head = {"Content-Type": "application/x-www-form-urlencoded", "token": i}#传token
            api=requests_single(url=data['url'],requersts_type=data['期望请求方式'],paramt=paramt,headers=i)

            api_json=api.getJson()#取返回joson值里面的值
            retMsg=api_json.get('retMsg')
            try:
                self.assertEqual(retMsg, '委托下单成功', msg='下单失败')
            except Exception as e:
                print(e)

            plan_order_id=api_json.get('retData').get('plan_order_id')#取出订单id
            sql_plan_order_id="SELECT * FROM `pc_order` WHERE order_id='%s'"%(plan_order_id)#根据订单id查询订单表
            print(sql_plan_order_id)
            plan_order=db_link.get_one(sql_plan_order_id)
            print('查询订单',plan_order)
            '''
                                              计算execl和落库的数据是否一致
                                   '''
            try:
                self.assertEqual(price, plan_order['price'], msg='下单价格跟数据库价格不一致')
                self.assertEqual(lever, plan_order['lever'], msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(bs_flag, plan_order['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(order_type, plan_order['order_type'], msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(order_type, plan_order['order_type'], msg='下单订单类型跟数据库价格不一致')
            except Exception as e:
                print(e)
            '''
          计算起始保证金
          '''
            amount=quantity*price/lever# 计算起始保证金
            try:
                self.assertEqual(round(amount,12),float(plan_order['amount']),msg='保证金不相等')#取出数据库的保证金，数据库中的保证金对比是否相等，如果有异常包住，继续
            except Exception as e:
                print(e)
            '''
            计算预收开仓手续费（预收开仓和平仓一致）
            计算预收平仓手续费
            '''
            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"#计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)
            taker_fee_ratio = quantity * price *float(symbol_BTC['taker_fee_ratio'])#取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
            try:
               #判断开仓手续费是否相等
                self.assertEqual(taker_fee_ratio,plan_order['open_fee'])
                # 判断平仓手续费是否相等
                self.assertEqual(taker_fee_ratio,plan_order['close_fee'])
            # 判断杠杆是否相等
                self.assertEqual(lever, plan_order['lever'])
            except Exception as e:
                print(e)
            '''
            计算账户扣减金额是否正确
            '''
            Balance = amount + taker_fee_ratio * 2
            print("下单金额", Balance)
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get', paramt=paramt, headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            keyong = usdt_Balance.get('retData').get('futures_usdt_balance')
            print('keyong',keyong)
            shengyu=float(totoal.replace(",",""))-float(keyong.replace(",",""))
            print(float(totoal.replace(",",""))-float(keyong.replace(",","")))
            print("剩余余额",shengyu)
            try:
                self.assertEqual(shengyu,Balance,msg='扣减额度不正确')
            except Exception as e:
                print(e)

            '''
          维持保证金 = 合约数量*开仓价格*维持保证金率
          '''
            weichi=quantity*price*maintenance
            print(weichi)

if __name__ == '__main__':
    unittest.main()
