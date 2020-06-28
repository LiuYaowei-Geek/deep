# coding=utf-8
import unittest
import time
from Interface.test_login import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
import requests
from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.get_execl import read_excel
from Interface.Character import Character_split
wenjian = EXECL_PATH + '\\cancel_order.xlsx'  #查询到对应的case文件
excel= read_excel(wenjian, '合仓撤单')
db_link=db_commit()
slice_Character=Character_split()#截取字符
#逐仓用户多次撤单校验
rise='315900'

url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
'''
逐仓用户多次撤单校验
'''
class Test_Login_Limit(unittest.TestCase):
    def setUp(self):
        LOG.info('限价买涨计算强平价开始')
    def tearDown(self):
        LOG.info('限价买涨计算强平价结束')

    def test_1_shuj(self):
        test = Test_Login(rise)
        token_test = test.test_log()
        '''
        取开多的数据
        '''
        data1_url = excel.exexl('url')  # 取url
        host_duo = data1_url[0]["url"]  # 取URL的第一个值
        pramnt_pramnt = excel.exexl('参数')  # 取url
        pramnt_duo = pramnt_pramnt[0]["参数"]
        pramnt1_dict_duo = eval(pramnt_duo)
        print(pramnt1_dict_duo)
        qingqiu_duo = excel.exexl('请求方式')  # 取url
        qingqiu_duo1 = qingqiu_duo[0]["请求方式"]
        # 取第二组数据
        host_duo2 = data1_url[1]["url"]  # 取URL的第一个值
        print(host_duo2)
        pramnt_duo2 = pramnt_pramnt[1]["参数"]

        pramnt2_dict_duo = eval(pramnt_duo2)
        print(pramnt2_dict_duo)
        qingqiu2_duo = qingqiu_duo[1]["请求方式"]
        # 取第三组数据
        host_duo3 = data1_url[2]["url"]  # 取URL的第一个值
        print(host_duo3)
        qingqiu3_duo = qingqiu_duo[2]["请求方式"]
        # 取第四组数据
        host_duo4 = data1_url[3]["url"]  # 取URL的第一个值
        print(host_duo4)
        qingqiu4_duo = qingqiu_duo[3]["请求方式"]

        # 取第五组数据
        host_duo5 = data1_url[4]["url"]  # 取URL的第一个值
        print(host_duo5)
        qingqiu5_duo = qingqiu_duo[4]["请求方式"]
        # 取第六组数据
        host_duo6 = data1_url[5]["url"]  # 取URL的第一个值
        print(host_duo6)
        qingqiu6_duo = qingqiu_duo[5]["请求方式"]

        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        for i in token_test['token']:
            print("-----------------------------------")
            type_c = token_test['contract_type']
            if type_c[0] ==1:  # 判断是否全仓还是逐仓

                contract_type = {"contract_type": '2'}  # 是全仓换成逐仓
                contract = requests_single(url='https://t01-mapi.deepcoin.pro/pc/set-contract-type',
                                           requersts_type='post', paramt=contract_type, headers=i)  # 切换仓位接口
                contract_list = contract.getJson()

            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)  # 查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print("查看总额度", totoal)
            # 下单
            api_json = requests_single(url=host_duo, requersts_type=qingqiu_duo1, paramt=pramnt1_dict_duo, headers=i)
            plan_order_id = api_json.getJson()
            order_Msg1 = plan_order_id.get('retMsg')  # 取出订单id
            plan_order1 = plan_order_id.get('retData').get('plan_order_id')
            try:
                self.assertEqual(order_Msg1, '委托下单成功', msg='委托下单失败')
            except Exception as e:
                print(e)
            sql_plan_order_id_to = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order1)  # 根据订单id查询订单表
            print(sql_plan_order_id_to)

            plan_order_to = db_link.get_one(sql_plan_order_id_to)

            print('查询订单', plan_order_to)
            '''
              计算execl和落库的数据是否一致
            '''
            amount = float(pramnt1_dict_duo['quantity']) * float(pramnt1_dict_duo['price']) / float(
                pramnt1_dict_duo['lever'])  # 计算起始保证金
            print('execl计算起始保证金', amount)
            self.assertEqual(pramnt1_dict_duo['price'], str(plan_order_to['price']).rstrip('0').strip('.'),
                             msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt1_dict_duo['lever'], str(plan_order_to['lever']).rstrip('0').strip('.'),
                             msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt1_dict_duo['bs_flag']), plan_order_to['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt1_dict_duo['order_type']), plan_order_to['order_type'],
                             msg='下单订单类型跟数据库价格不一致')
            self.assertEqual(round(amount, 4), float(plan_order_to['amount']), msg='保证金不相等')
            self.assertEqual(round(amount, 4), float(plan_order_to['amount']), msg='保证金不相等')

            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)
            taker_fee_ratio_1 = plan_order_to['quantity'] * plan_order_to['price'] * symbol_BTC[
                'taker_fee_ratio']  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
            try:
                # 判断开仓手续费是否相等
                self.assertEqual(taker_fee_ratio_1, plan_order_to['open_fee'])
                # 判断平仓手续费是否相等
                self.assertEqual(taker_fee_ratio_1, plan_order_to['close_fee'])
                # 判断杠杆是否相等
                self.assertEqual(taker_fee_ratio_1['lever'], plan_order_to['lever'])
            except Exception as e:
                print(e)

                # 下单第二组数据
            print('***********************************************************************************')
            api_json_2 = requests_single(url=host_duo2, requersts_type=qingqiu2_duo, paramt=pramnt2_dict_duo,
                                         headers=i)
            plan_order_id_2 = api_json_2.getJson()
            order_Msg_2 = plan_order_id_2.get('retMsg')  # 取出订单id
            plan_order_2 = plan_order_id_2.get('retData').get('plan_order_id')
            try:
                self.assertEqual(order_Msg_2, '委托下单成功', msg='委托下单失败')
            except Exception as e:
                print(e)
            sql_plan_order_id_to_2 = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order_2)  # 根据订单id查询订单表
            print(sql_plan_order_id_to_2)

            plan_order_to_2 = db_link.get_one(sql_plan_order_id_to_2)

            print('查询订单', plan_order_to_2)
            '''
              计算execl和落库的数据是否一致
            '''
            amount_3 = float(pramnt2_dict_duo['quantity']) * float(pramnt2_dict_duo['price']) / float(
                pramnt2_dict_duo['lever'])  # 计算起始保证金
            print('execl计算起始保证金', amount_3)
            print(type(plan_order_to_2['price']))

            self.assertEqual(pramnt2_dict_duo['price'], str(plan_order_to_2['price']).rstrip('0').strip('.'),
                             msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt2_dict_duo['lever'], str(plan_order_to_2['lever']).rstrip('0').strip('.'),
                             msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['bs_flag']), plan_order_to_2['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['order_type']), plan_order_to_2['order_type'],
                             msg='下单订单类型跟数据库价格不一致')
            self.assertEqual(round(amount_3, 4), float(plan_order_to_2['amount']), msg='保证金不相等')
            print('execl计算起始保证金', amount_3)
            self.assertEqual(pramnt2_dict_duo['price'], str(plan_order_to_2['price']).rstrip('0').strip('.'),
                             msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt2_dict_duo['lever'], str(plan_order_to_2['lever']).rstrip('0').strip('.'),
                             msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['bs_flag']), plan_order_to_2['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['order_type']), plan_order_to_2['order_type'],
                             msg='下单订单类型跟数据库价格不一致')

            taker_fee_ratio_2 = plan_order_to_2['quantity'] * plan_order_to_2['price'] * symbol_BTC[
                'taker_fee_ratio']  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率

            # 判断开仓手续费是否相等
            self.assertEqual(taker_fee_ratio_2, plan_order_to_2['open_fee'])
            # 判断平仓手续费是否相等
            self.assertEqual(taker_fee_ratio_2, plan_order_to_2['close_fee'])
            # 判断杠杆是否相等
            self.assertEqual(pramnt2_dict_duo['lever'], slice_Character.split_to(plan_order_to_2['lever']))
            time.sleep(2)


            #撤单一笔记录
            print('----------------------------------------------------------------------------------------------')
            paramt1={'order_id':plan_order1}
            api_json_3 = requests_single(url=host_duo3, requersts_type=qingqiu3_duo, paramt=paramt1,headers=i)
            plan_order_id_3 = api_json_3.getJson()
            plan_order_id_3.get('retMsg')
            # 撤单二笔记录
            print('----------------------------------------------------------------------------------------------')
            paramt1 = {'order_id': plan_order_2}
            api_json_4 = requests_single(url=host_duo3, requersts_type=qingqiu3_duo, paramt=paramt1, headers=i)
            plan_order_id_4 = api_json_4.getJson()
            plan_order_id_4.get('retMsg')

            print('***********************************************','第二次撤单','******************************************')
            # 撤单一笔记录
            print('----------------------------------------------------------------------------------------------')
            paramt3 = {'order_id': plan_order1}
            api_json_5 = requests_single(url=host_duo5, requersts_type=qingqiu5_duo, paramt=paramt3, headers=i)
            plan_order_id_5 = api_json_5.getJson()
            self.assertEqual(plan_order_id_5.get('retMsg'),'订单状态异常')
            # 撤单二笔记录
            print('----------------------------------------------------------------------------------------------')
            paramt4= {'order_id': plan_order_2}
            api_json6 = requests_single(url=host_duo6, requersts_type=qingqiu6_duo, paramt=paramt4, headers=i)
            plan_order_id_6 = api_json6.getJson()
            plan_order_id_6.get('retMsg')
            self.assertEqual(plan_order_id_6.get('retMsg'), '订单状态异常')
            '''
            撤单之后计算余额是否退回
            '''
            sql_usdt_Balance1 = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)  # 查看余额接口
            Balance1 = sql_usdt_Balance1.getJson()
            totoal_balancel = Balance1.get('retData').get('futures_usdt_balance')
            print("查看总额度", totoal)
            self.assertEqual(totoal,totoal_balancel,'额度不正确，撤单异常')
if __name__ == '__main__':
    unittest.main()