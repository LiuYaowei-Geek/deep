# coding=utf-8
import unittest
import ast
import ddt
import json
import time
from Interface.test_login import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
import requests
from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.get_execl import read_excel

wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
excel_kong = read_excel(wenjian,'合仓开空')
excel_duo = read_excel(wenjian,'合仓开多')
db_link=db_commit()
rise=315782
drop=316095
url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
'''
限价合仓开空+合仓开多
一个用户下两笔开多
一个用户下两笔开空
'''

class Test_Login_Open(unittest.TestCase):
    def setUp(self):
        LOG.info('合仓开空开始')

    def tearDown(self):
        LOG.info('合仓开空结束')



    '''
   合仓开空
   计算强评价
    注意：取参数时，需要查看execl是否有多余的空格
    :param data:
    :return:
    '''
    def test_1_Open_dir(self):
        test = Test_Login(rise)
        token_test = test.test_log()
        '''
                取开多的数据
                '''
        data1_url = excel_kong.exexl('url')  # 取url
        host_duo = data1_url[0]["url"]  # 取URL的第一个值
        pramnt_pramnt = excel_kong.exexl('参数')  # 取url
        pramnt_duo = pramnt_pramnt[0]["参数"]
        pramnt1_dict_duo = eval(pramnt_duo)
        print(pramnt1_dict_duo)
        qingqiu_duo = excel_kong.exexl('请求方式')  # 取url
        qingqiu_duo1 = qingqiu_duo[0]["请求方式"]
        # 取第二组数据
        host_duo2 = data1_url[1]["url"]  # 取URL的第一个值
        print(host_duo2)
        pramnt_duo2 = pramnt_pramnt[1]["参数"]

        pramnt2_dict_duo = eval(pramnt_duo2)
        print(pramnt2_dict_duo)
        qingqiu2_duo = qingqiu_duo[1]["请求方式"]
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        for i in token_test['token']:
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt="1111", headers=i)  # 查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print(i)
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
            try:

                self.assertEqual(pramnt1_dict_duo['price'], plan_order_to['price'], msg='参数1下单价格跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['lever'], plan_order_to['lever'], msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['bs_flag'], plan_order_to['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['order_type'], plan_order_to['order_type'], msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(round(amount, 4), float(plan_order_to['amount']), msg='保证金不相等')
            except Exception as e:
                print(e)

            print('----------------------------------------------------------------------------------------------')
            api_json1 = requests_single(url=host_duo2, requersts_type=qingqiu2_duo, paramt=pramnt2_dict_duo, headers=i)
            plan_order_id1 = api_json1.getJson()
            print(api_json1.url)
            order_Msg2 = plan_order_id1.get('retMsg')  # 取出订单id
            plan_order2 = plan_order_id1.get('retData').get('plan_order_id')
            print("订单id", plan_order_id)
            print("订单", order_Msg2)
            try:
                self.assertEqual(order_Msg2, '委托下单成功', msg='委托下单失败')
            except Exception as e:
                print(e)
            sql_plan_order_id = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order2)  # 根据订单id查询订单表
            print(sql_plan_order_id)

            plan_order = db_link.get_one(sql_plan_order_id)

            print('查2询订单', plan_order)
            '''
              计算execl和落库的数据是否一致
            '''
            amount = float(pramnt2_dict_duo['quantity']) * float(pramnt2_dict_duo['price']) / float(
                pramnt2_dict_duo['lever'])  # 计算起始保证金
            print('execl计算起始保证金', amount)
            try:

                self.assertEqual(pramnt2_dict_duo['price'], plan_order['price'], msg='参数1下单价格跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['lever'], plan_order['lever'], msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['bs_flag'], plan_order['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['order_type'], plan_order['order_type'], msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(round(amount, 4), float(plan_order['amount']), msg='保证金不相等')
                print('数据库保证金', plan_order['amount'])
            except Exception as e:
                print(e)
                # 合约数量 = 合约数量1+合约数量2

            quantity_duo = float(pramnt2_dict_duo['quantity']) + float(pramnt1_dict_duo['quantity'])
            print('合仓合约数量', quantity_duo)
            # 合约价值 = 合约数量1*开仓价格1+合约数量2*开仓价格2
            position_duo = float(pramnt2_dict_duo['quantity']) * float(pramnt2_dict_duo['price']) + float(
                pramnt1_dict_duo['quantity']) * float(pramnt1_dict_duo['price'])
            print('合仓仓位价值', position_duo)
            # 起始保证金
            Inital_margin_duo = position_duo / float(pramnt2_dict_duo['lever'])
            print('人为算出起始保证金', Inital_margin_duo)
            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)
            #计算平仓手续费
            taker_fee_ratio = float(quantity_duo) * float(position_duo) * float(
                symbol_BTC['taker_fee_ratio'])  # 取出taken手续费计算开仓保证金=开仓价格*数量*起始保证金率
            '''
                        计算账户扣减金额是否正确
                        '''
            Balance = Inital_margin_duo + taker_fee_ratio * 2
            print("下单金额", Balance)
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            keyong = usdt_Balance.get('retData').get('futures_usdt_balance')
            print('keyong', keyong)
            print(totoal, )
            shengyu = float(totoal) - float(keyong)
            print(float(totoal.replace(",", "")) - float(keyong.replace(",", "")))
            print("正确扣减的金额", shengyu)
            try:
                self.assertEqual(shengyu, Balance, msg='扣减额度不正确')
            except Exception as e:
                print(e)


    '''
    合仓开多
    计算强评价
    注意：取参数时，需要查看execl是否有多余的空格
    :param data:
    :return:
    '''
    def test_2_Open_many(self):

        test = Test_Login(drop)
        token_test = test.test_log()
        '''
        取开多的数据
        '''
        data1_duo_url = excel_duo.exexl('url')  # 取url
        host_duo = data1_duo_url[0]["url"]  # 取URL的第一个值
        pramnt_duo_pramnt = excel_duo.exexl('参数')  # 取url
        pramnt_duo = pramnt_duo_pramnt[0]["参数"]
        pramnt1_dict_duo = eval(pramnt_duo)
        print(pramnt1_dict_duo)
        qingqiu_duo = excel_duo.exexl('请求方式')  # 取url
        qingqiu_duo1 = qingqiu_duo[0]["请求方式"]
        # 取第二组数据
        host_duo2 = data1_duo_url[1]["url"]  # 取URL的第一个值
        print(host_duo2)
        pramnt_duo2 = pramnt_duo_pramnt[1]["参数"]

        pramnt2_dict_duo = eval(pramnt_duo2)
        print(pramnt2_dict_duo)
        qingqiu2_duo = qingqiu_duo[1]["请求方式"]
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        for i in token_test['token']:
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt="1111", headers=i)  # 查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print(i)
            api_json = requests_single(url=host_duo, requersts_type=qingqiu_duo1, paramt=pramnt1_dict_duo, headers=i)
            plan_order_id = api_json.getJson()
            order_Msg1 = plan_order_id.get('retMsg')  # 取出订单id
            plan_order1 = plan_order_id.get('retData').get('plan_order_id')
            try:
                self.assertEqual(order_Msg1, '委托下单成功', msg='委托下单失败')
            except Exception as e:
                print(e)
            sql_plan_order_id_to= "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order1)  # 根据订单id查询订单表
            print(sql_plan_order_id_to)

            plan_order_to = db_link.get_one(sql_plan_order_id_to)

            print('查询订单', plan_order_to)
            '''
              计算execl和落库的数据是否一致
            '''
            amount = float(pramnt1_dict_duo['quantity']) * float(pramnt1_dict_duo['price']) / float(
                pramnt1_dict_duo['lever'])  # 计算起始保证金
            print('execl计算起始保证金', amount)
            try:

                self.assertEqual(pramnt1_dict_duo['price'], plan_order_to['price'], msg='参数1下单价格跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['lever'], plan_order_to['lever'], msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['bs_flag'], plan_order_to['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(pramnt1_dict_duo['order_type'], plan_order_to['order_type'], msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(round(amount, 4), float(plan_order_to['amount']), msg='保证金不相等')
            except Exception as e:
                print(e)

            print('----------------------------------------------------------------------------------------------')
            api_json1 = requests_single(url=host_duo2, requersts_type=qingqiu_duo1, paramt=pramnt2_dict_duo, headers=i)
            plan_order_id1 = api_json1.getJson()
            print(api_json1.url)
            order_Msg2 = plan_order_id1.get('retMsg')  # 取出订单id
            plan_order2 = plan_order_id1.get('retData').get('plan_order_id')
            print("订单id", plan_order_id)
            print("订单", order_Msg2)
            try:
                self.assertEqual(order_Msg2, '委托下单成功', msg='委托下单失败')
            except Exception as e:
                print(e)
            sql_plan_order_id = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order2)  # 根据订单id查询订单表
            print(sql_plan_order_id)

            plan_order = db_link.get_one(sql_plan_order_id)

            print('查2询订单', plan_order)
            '''
              计算execl和落库的数据是否一致
            '''
            amount = float(pramnt2_dict_duo['quantity']) *float(pramnt2_dict_duo['price'])  / float(pramnt2_dict_duo['lever'])   # 计算起始保证金
            print('execl计算起始保证金',amount)
            try:

                self.assertEqual(pramnt2_dict_duo['price'], plan_order['price'], msg='参数1下单价格跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['lever'], plan_order['lever'], msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['bs_flag'], plan_order['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(pramnt2_dict_duo['order_type'], plan_order['order_type'], msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(round(amount, 4), float(plan_order['amount']), msg='保证金不相等')
                print('数据库保证金',plan_order['amount'])
            except Exception as e:
                print(e)
            '''
                    计算开多合仓数据2
                    '''
            # 合约数量 = 合约数量1+合约数量2

            quantity_duo = float(pramnt2_dict_duo['quantity']) + float(pramnt1_dict_duo['quantity'])
            print('合仓合约数量', quantity_duo)
            # 合约价值 = 合约数量1*开仓价格1+合约数量2*开仓价格2
            position_duo = float(pramnt2_dict_duo['quantity']) * float(pramnt2_dict_duo['price']) + float(
                pramnt2_dict_duo['quantity']) * float(pramnt1_dict_duo['price'])
            print('合仓仓位价值', position_duo)
            # 起始保证金
            Inital_margin_duo = position_duo / float(pramnt2_dict_duo['lever'])
            print('人为算出起始保证金', Inital_margin_duo)
            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)
            '''
            计算账户扣减金额是否正确
             '''
            #计算平仓手续费
            taker_fee_ratio = float(quantity_duo) * float(position_duo) * float(
                symbol_BTC['taker_fee_ratio'])  # 取出taken手续费计算开仓保证金=开仓价格*数量*起始保证金率
            '''
                        计算账户扣减金额是否正确
                        '''
            Balance = Inital_margin_duo + taker_fee_ratio * 2
            print("下单金额", Balance)
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt='1111', headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            keyong = usdt_Balance.get('retData').get('futures_usdt_balance')
            print('keyong', keyong)
            print(totoal, )
            shengyu = float(totoal) - float(keyong)
            print(float(totoal.replace(",", "")) - float(keyong.replace(",", "")))
            print("正确扣减的金额", shengyu)
            try:
                self.assertEqual(shengyu, Balance, msg='扣减额度不正确')
            except Exception as e:
                print(e)

    def test_3_Open_list(self):
        time.sleep(3)
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        sql_plan_order_id = "select * from  pc_order where uid in ('%s')"% (rise)  # 根据订单id查询订单表
        plan_order = db_link.get_all(sql_plan_order_id)
        print(type(plan_order))
        print(plan_order)
        # 判断状态是否是4持仓
        # 持仓订单id
        print(plan_order[0]['user_order_id'])
        print(plan_order[1]['user_order_id'])
        plan_order[1]['lever']
        print(plan_order[0]['amount']+plan_order[1]['amount'])
        print('--' * 50)
        order_status=plan_order[0]['order_status']
        print(plan_order[0]['quantity']+plan_order[1]['quantity'])
        if order_status == 4 or order_status == 3:
            # 查询pc_contract是taken还是maken
            symbo = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbo)
            # 查询持仓订单
            sql_trade_order_id = "select * from pc_trade_order where order_id in (select DISTINCT user_order_id from pc_order where uid in ('%s'))" % (rise)  # 根据订单id查询订单表
            print(sql_trade_order_id)
            order_id = db_link.get_one(sql_trade_order_id)
            # 起始保证金
            baozhengjin = (order_id['open_price'] * order_id['contract_qty']) / order_id['lever']
            try:
                # 判断起始保证金
                print('数据库起始保证金', order_id['amount'])
                self.assertEqual(round(baozhengjin, 4), order_id['amount'], msg='起始保证金数据不一致')
                # 判断杠杆
                self.assertEqual(plan_order[1]['lever'], order_id['lever'], msg='杠杆不一致')
            except Exception as e:
                print(e)
            '''
            开仓手续费
            '''
            sql_pc_match = "select * from pc_match where bid_order_id in ('%s');" % (order_id)  # 根据订单id查询订单表
            sql_pc_match1 = "select * from pc_match where ask_order_id in ('%s');" % (order_id)
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

            #bid_order_id
            if bid_uid!=None:
                if bid_uid['is_taker']==-1:
                    maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['maker_fee_ratio']
                    self.assertEqual(maker_amount,order_id['fee'],msg='maker开仓手续费不一致')
                elif bid_uid['is_taker']==1:
                    taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['taker_fee_ratio']
                    self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
            '''
            计算强平价
        '''
            print('方向', order_id['bs_flag'])
            if order_id['bs_flag'] == 2:
                # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)-追加保证金/合约数量+扣减保证金/合约数量
                duocang = order_id['open_price'] * (1 - 1 / order_id['lever'] + maintenance)
                print("多仓强平价格", duocang)
                try:
                    self.assertEqual(round(duocang, 4), order_id['force_price'], msg='多仓强平价格不一致')
                except Exception as e:
                    print(e)
            elif order_id['bs_flag'] == 1:
                # 空仓强平价格 = 开仓价格* (1+起始保证金率-维持保证金率)+追加保证金/合约数量-扣减保证金/合约数量
                kongcang = order_id['open_price'] * (1 + 1 / order_id['lever'] - maintenance)
                print("空仓强平价格", kongcang)
                print('数据库空仓强平价格', order_id['force_price'])
                try:
                    self.assertEqual(round(kongcang, 4), order_id['force_price'], msg='空仓强平价格不一致')
                except Exception as  e:
                    print(e)
            '''
           维持保证金 = 合约数量*开仓价格*维持保证金率
                          '''
            # weichi = quantity * price * maintenance
            # print(weichi)

            # 计算维持保证金
            weichi = (order_id['open_price'] * order_id[
                'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
            try:

                self.assertEqual(weichi, order_id['insurance_fund'], msg='维持保证金不一致')
                print(weichi, order_id['insurance_fund'])
            except Exception as e:
                print(e)

        else:
            LOG.info('用户持仓还未成交')
    def test_4_Open_list_to(self):
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
        sql_plan_order_id = "select * from  pc_order where uid in ('%s')" % (drop)  # 根据订单id查询订单表# 根据订单id查询订单表
        plan_order = db_link.get_all(sql_plan_order_id)
        print(type(plan_order))
        print(plan_order)
        # 判断状态是否是4持仓
        # 持仓订单id
        print(plan_order[0]['user_order_id'])
        print(plan_order[1]['user_order_id'])
        plan_order[1]['lever']
        print(plan_order[0]['amount']+plan_order[1]['amount'])
        print('--' * 50)
        order_status=plan_order[0]['order_status']
        print(plan_order[0]['quantity']+plan_order[1]['quantity'])
        if order_status == 4 or order_status == 3:
            # 查询pc_contract是taken还是maken
            symbo = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbo)
            # 查询持仓订单
            sql_trade_order_id = "select * from pc_trade_order where order_id in (select DISTINCT user_order_id from pc_order where uid in ('%s'))" % (drop)  # 根据订单id查询订单表
            print(sql_trade_order_id)
            order_id = db_link.get_one(sql_trade_order_id)
            # 起始保证金
            baozhengjin = (order_id['open_price'] * order_id['contract_qty']) / order_id['lever']
            try:
                # 判断起始保证金
                print('数据库起始保证金', order_id['amount'])
                self.assertEqual(round(baozhengjin, 4), order_id['amount'], msg='起始保证金数据不一致')
                # 判断杠杆
                self.assertEqual(plan_order[1]['lever'], order_id['lever'], msg='杠杆不一致')
            except Exception as e:
                print(e)
            '''
            开仓手续费
            '''
            sql_pc_match = "select * from pc_match where bid_order_id in ('%s');" % (plan_order[0]['order_id'])  # 根据订单id查询订单表
            sql_pc_match1 = "select * from pc_match where ask_order_id in ('%s');" % (plan_order[1]['order_id'])
            print(sql_pc_match)
            bid_uid = db_link.get_one(sql_pc_match)
            bid_uid1 = db_link.get_one(sql_pc_match1)

            if bid_uid1!=None:
                if bid_uid1['is_taker']==-1:
                    maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['taker_fee_ratio']
                    self.assertEqual(maker_amount,bid_uid1['fee'],msg='maker开仓手续费不一致')
                elif bid_uid1['is_taker']==1:
                    taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['maker_fee_ratio']
                    self.assertEqual(taker_amount, bid_uid1['fee'], msg='taker开仓手续费不一致')
                elif bid_uid1['is_taker']==None:
                    print('用户不是maker')

            #bid_order_id
            if bid_uid!=None:
                if bid_uid['is_taker']==-1:
                    maker_amount=order_id['open_price'] * order_id['contract_qty']*symbol_BTC['maker_fee_ratio']
                    self.assertEqual(maker_amount,bid_uid['fee'],msg='maker开仓手续费不一致')
                elif bid_uid['is_taker']==1:
                    taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC['taker_fee_ratio']
                    self.assertEqual(taker_amount, bid_uid['fee'], msg='taker开仓手续费不一致')
            else:
                print("用户有可能不是taker")
            '''
            计算强平价
        '''
            print('方向', order_id['bs_flag'])
            if order_id['bs_flag'] == 2:
                # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)-追加保证金/合约数量+扣减保证金/合约数量
                duocang = order_id['open_price'] * (1 - 1 / order_id['lever'] + maintenance)
                print("多仓强平价格", duocang)
                try:
                    self.assertEqual(round(duocang, 4), order_id['force_price'], msg='多仓强平价格不一致')
                except Exception as e:
                    print(e)
            elif order_id['bs_flag'] == 1:
                # 空仓强平价格 = 开仓价格* (1+起始保证金率-维持保证金率)+追加保证金/合约数量-扣减保证金/合约数量
                kongcang = order_id['open_price'] * (1 + 1 / order_id['lever'] - maintenance)
                print("空仓强平价格", kongcang)
                print('数据库空仓强平价格', order_id['force_price'])
                try:
                    self.assertEqual(round(kongcang, 4), order_id['force_price'], msg='空仓强平价格不一致')
                except Exception as  e:
                    print(e)
            '''
           维持保证金 = 合约数量*开仓价格*维持保证金率
                          '''
            # weichi = quantity * price * maintenance
            # print(weichi)

            # 计算维持保证金
            weichi = (order_id['open_price'] * order_id[
                'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率
            try:

                self.assertEqual(weichi, order_id['insurance_fund'], msg='维持保证金不一致')
                print(weichi, order_id['insurance_fund'])
            except Exception as e:
                print(e)

        else:
            LOG.info('用户持仓还未成交')

if __name__ == '__main__':
    unittest.main()
