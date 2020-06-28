# coding=utf-8
import unittest

import ddt
import json
from decimal import Decimal
from Interface.test_login import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
import requests
from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.get_execl import read_excel
import time
from Public.redis_value import redis_dta
from Interface.Character import Character_split
wenjian = EXECL_PATH + '\\set_lever.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'逐仓增加杠杆')
update_redis=redis_dta()#调用缓存方法，实例化类，调用方法

db_link=db_commit()#调用数据库
slice_Character=Character_split()#截取字符
single='315736'
url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json"}
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
'''
逐仓限价开多（减少杠杆）+逐仓强平价（减少杠杆）
一个用户开多开空，调整杠杆
'''
@ddt.ddt()
class Test_Loginrisr(unittest.TestCase):
    def setUp(self):
        LOG.info('逐仓追加保证金开始')
    def tearDown(self):
        LOG.info('逐仓追加保证金强结束')

    def test_1_shuj(self):
        test = Test_Login(single)
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
        #取第三组数据
        host_duo3 = data1_url[2]["url"]  # 取URL的第一个值
        print(host_duo3)
        pramnt_duo3 = pramnt_pramnt[2]["参数"]
        qingqiu3_duo = qingqiu_duo[2]["请求方式"]

        #取第四组数据
        host_duo4 = data1_url[3]["url"]  # 取URL的第一个值
        print(host_duo4)
        pramnt_duo4= pramnt_pramnt[3]["参数"]
        pramnt4_dict_duo = eval(pramnt_duo4)
        print(pramnt4_dict_duo)
        qingqiu4_duo = qingqiu_duo[3]["请求方式"]



        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        for i in token_test['token']:
            print("-----------------------------------")
            type_c = token_test['contract_type']
            if type_c[0] == 1:  # 判断是否全仓还是逐仓

                contract_type = {"contract_type": '2'}  # 是全仓换成逐仓
                contract = requests_single(url='https://t01-mapi.deepcoin.pro/pc/set-contract-type',
                                           requersts_type='post', paramt=contract_type, headers=i)  # 切换仓位接口
                contract_list = contract.getJson()
                contract_list.get('retData')['user']['contract_type']

            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)  # 查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print("查看总额度", totoal)
            #下单
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
            amount_1 = float(pramnt1_dict_duo['quantity']) * float(pramnt1_dict_duo['price']) / float(
                pramnt1_dict_duo['lever'])  # 计算起始保证金
            print('execl计算起始保证金', amount_1)
            self.assertEqual(pramnt1_dict_duo['price'], str(plan_order_to['price']).rstrip('0').strip('.'),
                             msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt1_dict_duo['lever'], str(plan_order_to['lever']).rstrip('0').strip('.'),
                             msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt1_dict_duo['bs_flag']), plan_order_to['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt1_dict_duo['order_type']), plan_order_to['order_type'],
                             msg='下单订单类型跟数据库价格不一致')
            self.assertEqual(round(amount_1, 4), float(plan_order_to['amount']), msg='保证金不相等')
            '''
                                  计算预收开仓手续费（预收开仓和平仓一致）
                                  计算预收平仓手续费
                                  '''
            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)
            taker_fee_ratio_1 = plan_order_to['quantity'] * plan_order_to['price'] * symbol_BTC['taker_fee_ratio']  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
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
            self.assertEqual(pramnt2_dict_duo['price'],slice_Character.split_to(plan_order_to_2['price']), msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt2_dict_duo['lever'],slice_Character.split_to(['lever']), msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['bs_flag']), plan_order_to_2['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['order_type']), plan_order_to_2['order_type'],
                             msg='下单订单类型跟数据库价格不一致')

            taker_fee_ratio_2 = plan_order_to_2['quantity'] * plan_order_to_2['price'] * symbol_BTC['taker_fee_ratio']  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
            try:
                # 判断开仓手续费是否相等
                self.assertEqual(taker_fee_ratio_2, plan_order_to_2['open_fee'])
                # 判断平仓手续费是否相等
                self.assertEqual(taker_fee_ratio_2, plan_order_to_2['close_fee'])
                # 判断杠杆是否相等
                self.assertEqual(pramnt2_dict_duo['lever'], plan_order_to_2['lever'])
            except Exception as e:
                print(e)
            #查询持仓列表
            print('----------------------------------------------------------------------------------------------')
            api_json3 = requests_single(url=host_duo3, requersts_type=qingqiu3_duo, paramt='11111', headers=i)
            plan_order_id3 = api_json3.getJson()
            for xia in range(0,2):
                 print(plan_order_id3.get('retData')['list'][xia])
                 plan_order3=[]
                 plan_order3.append(plan_order_id3.get('retData')['list'][xia]['order_id'])
                 before_price=plan_order_id3.get('retData')['list'][xia]['force_price']
                 print('调整前的强平价',before_price)
                 # 增加杠杆取第四组数据(增加两次杠杆)
                 print('-----------------------------------------------------------------------------------')
                 for s in plan_order3:
                     update_redis.redis_value('8500')
                     print(type(pramnt4_dict_duo))
                     dict_to = {'trade_order_id': s}
                     pr = {}
                     pr.update(pramnt4_dict_duo)
                     pr.update(dict_to)
                     api_json4 = requests_single(url=host_duo4, requersts_type=qingqiu4_duo, paramt=pr, headers=i)
                     req = api_json4.getJson()
                     req.get('retMsg')
                     # 查询持仓列表
                     print(
                         '----------------------------------------------------------------------------------------------')
                     api_json5 = requests_single(url=host_duo3, requersts_type=qingqiu3_duo, paramt='11111', headers=i)
                     plan_order_id5 = api_json5.getJson()
                     for xia1 in range(0, 1):
                         print("调整杠杆后的强评价", plan_order_id5.get('retData')['list'][xia1]['force_price'])
                     print("订单id", plan_order_id)
                     sql_trade_order_id = "select * from pc_trade_order where order_id  in ('%s')" % (str(s))  # 根据订单id查询订单表
                     print(sql_trade_order_id)
                     order_id = db_link.get_one(sql_trade_order_id)

    def test_2_strong(self):
        pramnt_pramnt = excel.exexl('参数')  # 取url
        pramnt_duo4 = pramnt_pramnt[3]["参数"]

        pramnt4_dict_duo = eval(pramnt_duo4)
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        sql_plan_order_id = "SELECT * FROM `pc_order` WHERE uid IN ('%s')" % (single)  # 根据订单id查询订单表
        plan_order = db_link.get_all(sql_plan_order_id)
        print(type(plan_order))
        print(plan_order)
        user_order_id = []
        lever = []
        order_status = []
        pc_order_id_wei = []
        # 判断状态是否是4持仓
        #循环数据库总条数，取值
        for i in range(0, 2):
            # 持仓订单id
            print(plan_order[i]['user_order_id'])#取pc_order表中的user_order_id
            user_order_id.append(plan_order[i]['user_order_id'])#把值放到list里面
            lever.append(plan_order[i]['lever'])#取pc_order表中的杠杆
            print('--' * 50)
            order_status.append(plan_order[i]['order_status'])
            pc_order_id_wei.append(plan_order[i]['order_id'])#取pc_order表中的状态
            print(lever)
            print("111", user_order_id)
        #取数据库里面的值进行对比
        for pc_order_id, s, order_status1, wei_order_id in zip(user_order_id, lever, order_status, pc_order_id_wei):#循环list里面的值
            print(order_status1)
            if order_status1 == 4 or order_status1 == 3:
                # 查询pc_contract是taken还是maken
                symbo = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
                symbol_BTC = db_link.get_one(symbo)

                print(s)
                # 查询持仓订单
                sql_trade_order_id = "select * from pc_trade_order where order_id  in ('%s')" % (
                    pc_order_id)  # 根据订单id查询订单表
                print(sql_trade_order_id)
                order_id = db_link.get_one(sql_trade_order_id)
                #判断数据库的杠杆是否跟execl一致
                print(pramnt4_dict_duo['lever'])
                print(order_id['lever'])
                try:
                    self.assertEqual(pramnt4_dict_duo['lever'],slice_Character.split_to(order_id['lever']),msg='execl追加的杠杆跟数据库的不一致')
                    # 起始保证金
                    global baozhengjin
                    baozhengjin = (order_id['open_price'] * order_id['contract_qty']) / order_id['lever']
                except Exception as e:
                    print(e)
                try:
                    # 判断起始保证金
                    print('数据库起始保证金', order_id['amount'])
                    self.assertEqual(slice_Character.split_to(baozhengjin), slice_Character.split_to(order_id['amount']), msg='起始保证金数据不一致')
                    # 判断杠杆
                    self.assertEqual(s, order_id['lever'], msg='杠杆不一致')
                except Exception as e:
                    print(e)
                '''
                开仓手续费
                '''
                sql_pc_match= "select * from pc_match where bid_order_id in ('%s');" % (wei_order_id)  # 根据订单id查询订单表
                sql_pc_match1 = "select * from pc_match where ask_order_id in ('%s');" % (wei_order_id)
                print(sql_pc_match)
                bid_uid = db_link.get_one(sql_pc_match)
                bid_uid1 = db_link.get_one(sql_pc_match1)
                if bid_uid1!=None:
                    if bid_uid1['is_taker']==-1:
                        maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['taker_fee_ratio']
                        self.assertEqual(maker_amount,order_id['fee'],msg='maker开仓手续费不一致')
                    elif bid_uid1['is_taker']==1:
                        taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['maker_fee_ratio']
                        self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                    elif bid_uid1['is_taker']==None:
                        print('用户不是aker')
                else:
                    print("有可能用户不是taker")

                #bid_order_id
                if bid_uid!=None:
                    if bid_uid['is_taker']==-1:
                        maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['maker_fee_ratio']
                        self.assertEqual(maker_amount,order_id['fee'],msg='maker开仓手续费不一致')
                    elif bid_uid['is_taker']==1:
                        taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['taker_fee_ratio']
                        self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                else:
                    print("有可能用户不是maker")
                # 计算维持保证金
                weichi = (order_id['open_price'] * order_id[
                    'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*维持保证金率
                try:

                    self.assertEqual(slice_Character.split_Four(weichi), slice_Character.split_Four(order_id['insurance_fund']), msg='维持保证金不一致')
                    print(weichi, order_id['insurance_fund'])
                except Exception as e:
                    print(e)
                '''
                计算强平价
            '''
                print('方向', order_id['bs_flag'])
                if order_id['bs_flag'] == 2:
                    print('起始保证金率+维持保证金',1-1/order_id['lever']+maintenance )
                    print('开仓价格',order_id['open_price'])
                    print(order_id['extra_margin']/order_id['contract_qty'])

                    # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)
                    duocang = order_id['open_price'] * (1-1/order_id['lever']+maintenance )

                    self.assertEqual(slice_Character.split_to(duocang), slice_Character.split_to(order_id['force_price']), msg='多仓强平价格不一致')

                elif order_id['bs_flag'] == 1:
                    #空仓强平价格 = 开仓价格 * (1 + 起始保证金率 - 维持保证金率)
                    kongcang = order_id['open_price'] *(1+1/order_id['lever']-maintenance)
                    print("空仓强平价格", kongcang)
                    print('数据库空仓强平价格', order_id['force_price'])

                    self.assertEqual(slice_Character.split_to(kongcang), slice_Character.split_to(order_id['force_price']), msg='空仓强平价格不一致')


            else:
                LOG.info('用户持仓还未成交')

if __name__ == '__main__':
    unittest.main()
