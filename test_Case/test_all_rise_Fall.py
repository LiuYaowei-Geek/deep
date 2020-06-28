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
from Public.read_excel import read_excel
from Interface.Character import Character_split

import time
wenjian = EXECL_PATH + '\\all_create_order.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'全仓限价开多+开空强平价')
excel_drop = read_excel(wenjian,'全仓限价开多')
db_link=db_commit()
single='315768'
single_to='315915'

url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
slice_Character=Character_split()#截取字符
'''
全仓限价开多+开空强平价
一个用户开多+开空
另一个用户开多
'''
@ddt.ddt()
class Test_Loginrisr(unittest.TestCase):
    def setUp(self):
        LOG.info('全仓限价开多+开空强平价开始')
    def tearDown(self):
        LOG.info('全仓限价开多+开空强平价介绍')

    @ddt.data(*excel.next())
    def test_1_shuj(self,data):
        '''
        计算强评价
        维持保证金
        注意：取参数时，需要查看execl是否有多余的空格
        :param data:
        :return:
        '''

        test = Test_Login(single)
        token_test = test.test_log()
        quantity=float(data['quantity(数量)'])
        lever=int(data['lever(杠杆)'])
        bs_flag=int(data['bs_flag(1买跌/2买涨)'])
        price=data['price(限价单)']
        order_type=int(data['order_type(订单类型1市场 2限价)'])
        contract_id=data['contract_id(交易对)']
        paramt_type=data['期望请求方式']
        #1、市场价买涨算强平价格计算
        #2、多仓强平价格 = 开仓价格 * (1 - 起始保证金率 + 维持保证金率)
        #查询维持保证金率
        sql=('SELECT * FROM pc_risk_limit')
        maintenance_margin=db_link.get_one(sql)#查询维持保证金率第一条数据
        maintenance=float(maintenance_margin['maintenance_margin_rate'])#取出维持保证金率
        # #起始保证金率(1 - 1 / lever)
        Strong_parity=price*(1-1/lever+maintenance)
        print('强平价',Strong_parity)


        paramt={'quantity':quantity,'lever':lever,'bs_flag':bs_flag,'price':price,'order_type':order_type,'contract_id':contract_id,'price':price} #拼接参数
        print(paramt)
        print(type(token_test['token']))
        for i in  token_test['token']:#循环里面token_test的值
            type_c = token_test['contract_type']
            print(type_c)
            if type_c[0] == 2:  # 判断是否全仓还是逐仓

                contract_type = {"contract_type": '1'}  # 是逐仓切换成全仓
                contract=requests_single(url='https://t01-mapi.deepcoin.pro/pc/set-contract-type', requersts_type='post', paramt=contract_type, headers=i)#切换仓位接口
                print(contract.getJson())
            print(i)
            sql_usdt_Balance =requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance',requersts_type='get',paramt=paramt,headers=i)#查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print("查看总额度",totoal)

            head = {"Content-Type": "application/x-www-form-urlencoded", "token": i}#传token
            create_order_api=requests_single(url=data['url'],requersts_type=data['期望请求方式'],paramt=paramt,headers=i)#委托下单接口

            create_order_api_json=create_order_api.getJson()#取返回joson值里面的值
            retMsg=create_order_api_json.get('retMsg')
            try:
                self.assertEqual(retMsg, '委托下单成功', msg='下单失败')
            except Exception as e:
                print(e)

            plan_order_id=create_order_api_json.get('retData').get('plan_order_id')#取出订单id
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
            symbol_BTC = db_link.get_one(symbol)#取taker
            taker_fee_ratio = quantity * price *float(symbol_BTC['taker_fee_ratio'])#计算开仓保证金.开仓价格*数量*起始保证金率
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
            print(totoal,)
            shengyu=float(totoal)-float(keyong)
            print(float(totoal.replace(",",""))-float(keyong.replace(",","")))
            print("正确扣减的金额",shengyu)
            try:
                self.assertEqual(shengyu,Balance,msg='扣减额度不正确')
            except Exception as e:
                print(e)
            '''
          维持保证金 = 合约数量*开仓价格*维持保证金率
          '''
            weichi=quantity*price*maintenance
            print("维持保证金",weichi)

    @ddt.data(*excel_drop.next())
    def test_2_dirop(self, data):
        '''
        计算强评价
        维持保证金
        注意：取参数时，需要查看execl是否有多余的空格
        :param data:
        :return:
        '''

        test = Test_Login(single_to)
        token_test = test.test_log()
        quantity = float(data['quantity(数量)'])
        lever = int(data['lever(杠杆)'])
        bs_flag = int(data['bs_flag(1买跌/2买涨)'])
        price = data['price(限价单)']
        order_type = int(data['order_type(订单类型1市场 2限价)'])
        contract_id = data['contract_id(交易对)']
        paramt_type = data['期望请求方式']
        # 1、市场价买涨算强平价格计算
        # 2、多仓强平价格 = 开仓价格 * (1 - 起始保证金率 + 维持保证金率)
        # 查询维持保证金率
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = float(maintenance_margin['maintenance_margin_rate'])  # 取出维持保证金率
        # #起始保证金率(1 - 1 / lever)
        Strong_parity = price * (1 - 1 / lever + maintenance)
        print('强平价', Strong_parity)

        paramt = {'quantity': quantity, 'lever': lever, 'bs_flag': bs_flag, 'price': price, 'order_type': order_type,
                  'contract_id': contract_id, 'price': price}  # 拼接参数
        print(paramt)
        print(type(token_test['token']))
        for i in token_test['token']:  # 循环里面token_test的值
            type_c = token_test['contract_type']
            print(type_c)
            if type_c[0] == 2:  # 判断是否全仓还是逐仓

                contract_type = {"contract_type": '1'}  # 是逐仓切换成全仓
                contract = requests_single(url='https://t01-mapi.deepcoin.pro/pc/set-contract-type',
                                           requersts_type='post', paramt=contract_type, headers=i)  # 切换仓位接口
                print(contract.getJson())
            print(i)
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt=paramt, headers=i)  # 查看余额接口
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print("查看总额度", totoal)

            head = {"Content-Type": "application/x-www-form-urlencoded", "token": i}  # 传token
            create_order_api = requests_single(url=data['url'], requersts_type=data['期望请求方式'], paramt=paramt,
                                               headers=i)  # 委托下单接口

            create_order_api_json = create_order_api.getJson()  # 取返回joson值里面的值
            retMsg = create_order_api_json.get('retMsg')
            try:
                self.assertEqual(retMsg, '委托下单成功', msg='下单失败')
            except Exception as e:
                print(e)

            plan_order_id = create_order_api_json.get('retData').get('plan_order_id')  # 取出订单id
            sql_plan_order_id = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order_id)  # 根据订单id查询订单表
            print(sql_plan_order_id)
            plan_order = db_link.get_one(sql_plan_order_id)
            print('查询订单', plan_order)
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
            amount = quantity * price / lever  # 计算起始保证金
            try:
                self.assertEqual(round(amount, 12), float(plan_order['amount']),
                                 msg='保证金不相等')  # 取出数据库的保证金，数据库中的保证金对比是否相等，如果有异常包住，继续
            except Exception as e:
                print(e)
            '''
            计算预收开仓手续费（预收开仓和平仓一致）
            计算预收平仓手续费
            '''
            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，取taker来计算的
            symbol_BTC = db_link.get_one(symbol)  # 取taker
            taker_fee_ratio = quantity * price * float(symbol_BTC['taker_fee_ratio'])  # 计算开仓保证金.开仓价格*数量*起始保证金率
            try:
                # 判断开仓手续费是否相等
                self.assertEqual(taker_fee_ratio, plan_order['open_fee'])
                # 判断平仓手续费是否相等
                self.assertEqual(taker_fee_ratio, plan_order['close_fee'])
                # 判断杠杆是否相等
                self.assertEqual(lever, plan_order['lever'])
            except Exception as e:
                print(e)
            '''
            计算账户扣减金额是否正确
            '''
            Balance = amount + taker_fee_ratio * 2
            print("下单金额", Balance)
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt=paramt, headers=i)
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
          维持保证金 = 合约数量*开仓价格*维持保证金率
          '''
            weichi = quantity * price * maintenance
            print("维持保证金", weichi)
    def test_3_strong(self):
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
                # 起始保证金
                baozhengjin = (order_id['open_price'] * order_id['contract_qty']) / order_id['lever']
                try:
                    # 判断起始保证金
                    print('数据库起始保证金', order_id['amount'])
                    self.assertEqual(round(baozhengjin, 4), order_id['amount'], msg='起始保证金数据不一致')
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
                #计算维持保证金
                weichi = (order_id['open_price'] * order_id[
                    'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*维持保证金率
                try:

                    self.assertEqual(weichi, order_id['insurance_fund'], msg='维持保证金不一致')
                    print(weichi, order_id['insurance_fund'])
                except Exception as e:
                    print(e)

            else:
                LOG.info('用户持仓还未成交')

    def test_4_list_Strong(self):
        sql_trade_order_id = "select * from pc_trade_order where uid  in ('%s')" % (rise)
        print(sql_trade_order_id)
        order_id = db_link.get_all(sql_trade_order_id)
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率

        '''
         #计算余额
        '''
        rise_fund_user = "select * from fund_user t where uid in ('%s')" % (rise)
        sele_rise_user = db_link.get_one(rise_fund_user)
        for i in range(0, len(order_id)):
            if order_id[i]['bs_flag'] == 2:
                global rist_list
                rist_list = {'force_price': order_id[i]['force_price'], 'contract_qty': order_id[i]['contract_qty'],
                             'open_price': order_id[i]['open_price'],
                             'insurance_fund': order_id[i]['insurance_fund'], 'amount': order_id[i]['amount']}
                print(rist_list)
                '''
                       维持保证金
                      '''
                global rist_weichi
                rist_weichi = (rist_list['open_price'] * rist_list[
                    'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*维持保证金率
                try:

                    self.assertEqual(rist_weichi, rist_list['insurance_fund'], msg='维持保证金不一致')
                    print(rist_weichi, rist_list['insurance_fund'])
                except Exception as e:
                    print(e)
            elif order_id[i]['bs_flag'] == 1:
                global drop_list
                drop_list = {'force_price': order_id[i]['force_price'], 'contract_qty': order_id[i]['contract_qty'],
                             'open_price': order_id[i]['open_price'],
                             'insurance_fund': order_id[i]['insurance_fund'], 'amount': order_id[i]['amount']}
                print(drop_list)
                '''
                                       维持保证金
                             '''
                global drop_weichi

                drop_weichi = (drop_list['open_price'] * drop_list[
                    'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*维持保证金率
                try:

                    self.assertEqual(drop_weichi, drop_list['insurance_fund'], msg='维持保证金不一致')
                    print(drop_weichi, drop_list['insurance_fund'])
                except Exception as e:
                    print(e)
                    # 计算余额
                global rise_Balance
                rise_Balance = sele_rise_user['futures_usdt_balance'] + rist_list['amount'] + drop_list['amount'] + \
                               sele_rise_user['futures_usdt_freeze']
                # 多空仓强平价 = （多仓维持保证金+空仓维持保证金+多仓合约数量*多仓开仓价格-空仓合约数量*空仓开仓价格-余额）/（多仓合约数量-空仓合约数量）

        Strong = (rist_weichi + drop_weichi + rist_list['open_price'] * rist_list['contract_qty'] - drop_list[
            'open_price'] * drop_list['contract_qty'] - rise_Balance) / \
                 (rist_list['contract_qty'] - drop_list['contract_qty'])
        print("强平价", Strong)
        order_force = db_link.get_all(sql_trade_order_id)
        for f in range(0, len(order_force)):
            if order_force[i]['bs_flag'] == 2:
                self.assertEqual(slice_Character.split_to(Strong),
                                 slice_Character.split_to(order_force[f]['force_price']), msg='多仓强平价格不一致')
            elif order_force[i]['bs_flag'] == 1:
                self.assertEqual(slice_Character.split_to(Strong),
                                 slice_Character.split_to(order_force[f]['force_price']), msg='多仓强平价格不一致')


if __name__ == '__main__':
    unittest.main()
