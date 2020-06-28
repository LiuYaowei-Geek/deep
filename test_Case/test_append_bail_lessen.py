# coding=utf-8
import unittest

import ddt
import json
from Interface.test_login import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
import requests
from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.get_execl import read_excel
import time
wenjian = EXECL_PATH + '\\append_bail.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'减少保证金')
db_link=db_commit()
single='316173'
url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
'''
逐仓限价开多（减少保证金）+逐仓强平价（减少保证金）
一个用户开多开空，追加保证金，然后减少保证金
'''
@ddt.ddt()
class Test_Loginrisr(unittest.TestCase):
    def setUp(self):
        LOG.info('逐仓减少保证金开始')
    def tearDown(self):
        LOG.info('逐仓减少保证金强结束')

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
        # 取第五组数据
        host_duo5 = data1_url[4]["url"]  # 取URL的第一个值
        print(host_duo5)
        pramnt_duo5 = pramnt_pramnt[4]["参数"]

        pramnt5_dict_duo = eval(pramnt_duo5)
        print(pramnt5_dict_duo)
        qingqiu5_duo = qingqiu_duo[4]["请求方式"]



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
                print(contract_list)
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

            self.assertEqual(pramnt2_dict_duo['price'],str(plan_order_to_2['price']).rstrip('0').strip('.'), msg='参数1下单价格跟数据库价格不一致')
            self.assertEqual(pramnt2_dict_duo['lever'], str(plan_order_to_2['lever']).rstrip('0').strip('.'), msg='下单杠杆跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['bs_flag']), plan_order_to_2['bs_flag'], msg='下单方向跟数据库价格不一致')
            self.assertEqual(int(pramnt2_dict_duo['order_type']), plan_order_to_2['order_type'],
                             msg='下单订单类型跟数据库价格不一致')
            self.assertEqual(round(amount_3, 4), float(plan_order_to_2['amount']), msg='保证金不相等')

            taker_fee_ratio_2 = plan_order_to_2['quantity'] * plan_order_to_2['price'] * symbol_BTC[
                'taker_fee_ratio']  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率

            # 判断开仓手续费是否相等
            self.assertEqual(taker_fee_ratio_2, plan_order_to_2['open_fee'])
            # 判断平仓手续费是否相等
            self.assertEqual(taker_fee_ratio_2, plan_order_to_2['close_fee'])
            # 判断杠杆是否相等
            self.assertEqual(pramnt2_dict_duo['lever'], plan_order_to_2['lever'])

            time.sleep(2)
            #查询持仓金额
            print('----------------------------------------------------------------------------------------------')
            api_json3 = requests_single(url=host_duo3, requersts_type=qingqiu3_duo, paramt='11111', headers=i)
            plan_order_id3 = api_json3.getJson()
            print(api_json3.url)
            plan_order3=[]
            print(type(plan_order_id3))
            print(plan_order_id3)
            for xia in range(0,2):
                 plan_order3.append(plan_order_id3.get('retData')[xia].get('order_id'))
                 print("追加保证金前的强平金额", plan_order_id3.get('retData')[xia]['force_price'])
            print("订单id", plan_order_id)
            #取第四组数据追加保证金
            print('-----------------------------------------------------------------------------------')
            for s in plan_order3:

                print(type(pramnt4_dict_duo))
                dict_to={'trade_order_id':s}
                pr={}
                pr.update(pramnt4_dict_duo)
                pr.update(dict_to)
                api_json4 = requests_single(url=host_duo4, requersts_type=qingqiu4_duo, paramt=pr, headers=i)
                req=api_json4.getJson()
                req.get('retMsg')


            # 取第五组数据减少保证金
            print('-----------------------------------------------------------------------------------')
            for f in plan_order3:

                print(type(pramnt5_dict_duo))
                dict_to={'trade_order_id':f}
                pr1={}
                pr1.update(pramnt5_dict_duo)
                pr1.update(dict_to)
                api_json5 = requests_single(url=host_duo5, requersts_type=qingqiu5_duo, paramt=pr1, headers=i)
                req=api_json5.getJson()
                req.get('retMsg')
            Balance = (amount + amount_3) + float((taker_fee_ratio_1 + taker_fee_ratio_2) * 2) + (float(pramnt4_dict_duo['margin_amount']) * 2)-(float(pramnt5_dict_duo['margin_amount']) * 2)
            print("下单金额", Balance)
            #查询余额
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            keyong = usdt_Balance.get('retData').get('futures_usdt_balance')
            print('keyong', keyong)
            print(totoal, )
            shengyu = float(totoal) - float(keyong)
            print(float(totoal.replace(",", "")) - float(keyong.replace(",", "")))
            print("正确扣减的金额", shengyu)
            self.assertEqual(shengyu, Balance, msg='扣减额度不正确')

    def test_2_strong(self):
        pramnt_pramnt = excel.exexl('参数')  # 取url
        #追加保证金前的数据
        pramnt_duo4 = pramnt_pramnt[3]["参数"]
        pramnt4_dict_duo = eval(pramnt_duo4)
        #减少保证金
        pramnt_duo5 = pramnt_pramnt[4]["参数"]  # 取第四个参数
        pramnt5_dict_duo = eval(pramnt_duo5)


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

        for i in range(0, 2):
            # 持仓订单id
            print(plan_order[i]['user_order_id'])
            user_order_id.append(plan_order[i]['user_order_id'])
            lever.append(plan_order[i]['lever'])
            print('--' * 50)
            order_status.append(plan_order[i]['order_status'])
            pc_order_id_wei.append(plan_order[i]['order_id'])
            print(lever)
            print("111", user_order_id)
        for pc_order_id, s, order_status1, wei_order_id in zip(user_order_id, lever, order_status, pc_order_id_wei):
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
                print(pramnt5_dict_duo['margin_amount'])
                print(order_id['extra_margin'])
                if order_id['extra_cost']!=None:
                    price = int(pramnt4_dict_duo['margin_amount']) - int(pramnt5_dict_duo['margin_amount'])
                    self.assertEqual(str(price), str(order_id['extra_margin']).rstrip('0').strip('.'),
                                     msg='数据库减少的保证金跟execl的不一致')

                else:
                    print("减少保证金字段没有值")

                # 起始保证金
                baozhengjin = (order_id['open_price'] * order_id['contract_qty']) / order_id['lever']

                print('数据库起始保证金', order_id['amount'])
                try:
                    self.assertEqual(str(baozhengjin).rstrip('0').strip('.'),
                                     str(order_id['amount']).rstrip('0').strip('.'), msg='起始保证金数据不一致')
                except Exception as e:
                    print(e)
                # 判断杠杆
                self.assertEqual(s, order_id['lever'], msg='杠杆不一致')

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
                        makeramount=str(maker_amount).split('.')
                        makeramount1=makeramount[0]+'.'+makeramount[1][:2]
                        self.assertEqual(makeramount1, str(order_id['fee']).rstrip('0').strip('.'),msg='maker开仓手续费不一致')
                    elif bid_uid1['is_taker']==1:

                        taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['maker_fee_ratio']
                        self.assertEqual(str(taker_amount).rstrip('0').strip('.'),str(order_id['fee']).rstrip('0').strip('.') , msg='taker开仓手续费不一致')
                    elif bid_uid1['is_taker']==None:
                        print('用户不是maker')
                else:
                    print("有可能用户不是maker")

                #bid_order_id
                if bid_uid!=None:
                    if bid_uid['is_taker']==-1:
                        maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['maker_fee_ratio']

                        self.assertEqual(str(maker_amount).rstrip('0').strip('.'),str(order_id['fee']).rstrip('0').strip('.'),msg='maker开仓手续费不一致')
                        print(self.assertEqual(maker_amount,order_id['fee'],msg='maker开仓手续费不一致'))
                    elif bid_uid['is_taker']==1:
                        taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['taker_fee_ratio']
                        self.assertEqual(str(taker_amount).rstrip('0').strip('.'), str(order_id['fee']).rstrip('0').strip('.'), msg='taker开仓手续费不一致')
                else:
                    print("有可能用户不是taker")
                # 计算维持保证金
                weichi = (order_id['open_price'] * order_id[
                    'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*维持保证金率

                self.assertEqual(str(weichi).rstrip('0').strip('.'), str(order_id['insurance_fund']).rstrip('0').strip('.'),msg='维持保证金不一致')
                print(weichi, order_id['insurance_fund'])
                '''
                计算强平价
            '''
                print('方向', order_id['bs_flag'])
                if order_id['bs_flag'] == 2:


                    # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)-追加保证金/合约数量+扣减保证金/合约数量
                    duocang =float(order_id['open_price']) * (1-1/float(order_id['lever'])+float(maintenance))-float(pramnt4_dict_duo['margin_amount'])/float(order_id['contract_qty'])+float(pramnt5_dict_duo['margin_amount'])/float(order_id['contract_qty'])
                    print("多仓强平价格", duocang)
                    duo=str(duocang).split('.')
                    duo1=duo[0]+'.'+duo[1][:2]
                    self.assertEqual(duo1, str(order_id['force_price']).rstrip('0').strip('.'), msg='多仓强平价格不一致')
                elif order_id['bs_flag'] == 1:
                    #空仓强平价格 = 开仓价格 * (1 + 起始保证金率 - 维持保证金率) + 追加保证金 / 合约数量 - 扣减保证金 / 合约数量
                    print(type(pramnt5_dict_duo['margin_amount']))
                    print(type(maintenance))
                    print(type(order_id['open_price']))
                    kongcang = float(order_id['open_price'])*float((1+1/order_id['lever']-maintenance))+float(pramnt4_dict_duo['margin_amount'])/float(order_id['contract_qty'])-float(pramnt5_dict_duo['margin_amount'])/float(order_id['contract_qty'])
                    print("空仓强平价格", kongcang)
                    print('数据库空仓强平价格', order_id['force_price'])
                    kong=str(kongcang).split('.')
                    kong1=kong[0]+'.'+kong[1][:2]

                    self.assertEqual(kong1, str(order_id['force_price']).rstrip('0').strip('.'), msg='空仓强平价格不一致')
            else:
                LOG.info('用户持仓还未成交')

if __name__ == '__main__':
    unittest.main()
