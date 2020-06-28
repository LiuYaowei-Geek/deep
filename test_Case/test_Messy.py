from Public.log import LOG
from Interface.tese_requests_single import requests_single
from Public.read_excel import read_excel
from Interface.test_login import Test_Login
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit
from Interface.Character import Character_split
import ddt
slice_Character=Character_split()#截取字符
db_link=db_commit()
rise='315702'
wenjian = EXECL_PATH + '\\creata_interface.xlsx'  #查询到对应的case文件

excel_zhang = read_excel(wenjian, '限价买涨')
import unittest
@ddt.ddt
class Test_order_Limit(unittest.TestCase):
    def setUp(self):
        LOG.info('限价买涨计算强平价开始')
    def tearDown(self):
        LOG.info('限价买涨计算强平价结束')

    @ddt.data(*excel_zhang.next())
    def test_order_Limit(self,data):
        test = Test_Login(rise)
        token_test = test.test_log()
        quantity = float(data['quantity(数量)'])
        lever = float(data['lever(杠杆)'])
        bs_flag = int(data['bs_flag(1买跌/2买涨)'])
        price = data['price(限价单)']
        order_type = int(data['order_type(订单类型1市场 2限价)'])
        contract_id = data['contract_id(交易对)']
        print(lever)
        paramt = {'quantity': quantity, 'lever': lever, 'bs_flag': bs_flag, 'price': price, 'order_type': order_type,
                  'contract_id': contract_id}  # 拼接参数
        print(paramt)
        for i in token_test['token']:  # 循环里面token_test的值
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                               paramt=paramt, headers=i)
            usdt_Balance = sql_usdt_Balance.getJson()
            totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
            print(i)
            head = {"Content-Type": "application/x-www-form-urlencoded", "token": i}  # 传token
            api = requests_single(url=data['url'], requersts_type=data['期望请求方式'], paramt=paramt, headers=i)
            api_json = api.getJson()  # 0
            retMsg = api_json.get('retMsg')
            try:
                self.assertEqual(retMsg, '委托下单成功', msg='下单失败')
            except Exception as e:
                print(e)
            #判断是否下单成功
            if retMsg=='委托下单成功':
                sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                                   paramt=paramt, headers=i)
                usdt_Balance = sql_usdt_Balance.getJson()
                totoal = usdt_Balance.get('retData').get('futures_usdt_balance')
                print('查询用户总余额',totoal)

                sql = ('SELECT * FROM pc_risk_limit')
                maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
                maintenance = maintenance_margin['maintenance_margin_rate']  # 取出维持保证金率
                sql_plan_order_id = "SELECT * FROM `pc_order` WHERE uid IN ('%s')" % (rise)  # 根据订单id查询订单表
                plan_order = db_link.get_all(sql_plan_order_id)
                print('长度类型',type(plan_order))
                print(plan_order)
                user_order_id = []
                lever = []
                order_status = []
                pc_order_id_wei = []
                # 判断状态是否是4持仓
                print(len(plan_order))
                for i in range(0,len(plan_order)):
                    # 持仓订单id
                    print(plan_order[i]['user_order_id'])
                    user_order_id.append(plan_order[i]['user_order_id'])
                    lever.append(plan_order[i]['lever'])
                    print('--' * 50)
                    order_status.append(plan_order[i]['order_status'])
                    pc_order_id_wei.append(plan_order[i]['order_id'])
                    print(lever)
                    print("111", user_order_id)
                for pc_order_id, s, order_status1, wei_order_id in zip(user_order_id, lever, order_status,
                                                                       pc_order_id_wei):
                    print(order_status1)
                    if order_status1 == 4:
                        LOG.info('用户撮合成功')
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

                        # 判断起始保证金
                        print('数据库起始保证金', order_id['amount'])
                        self.assertEqual(slice_Character.split_Four(baozhengjin),
                                         slice_Character.split_Four(order_id['amount']), msg='起始保证金数据不一致')
                        # 判断杠杆
                        self.assertEqual(s, order_id['lever'], msg='杠杆不一致')
                        '''
                        开仓手续费
                        '''
                        sql_pc_match = "select * from pc_match where bid_order_id in ('%s');" % (
                        wei_order_id)  # 根据订单id查询订单表
                        sql_pc_match1 = "select * from pc_match where ask_order_id in ('%s');" % (wei_order_id)
                        print(sql_pc_match)
                        bid_uid = db_link.get_one(sql_pc_match)
                        bid_uid1 = db_link.get_one(sql_pc_match1)

                        if bid_uid1 != None:
                            if bid_uid1['is_taker'] == -1:
                                maker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'taker_fee_ratio']
                                self.assertEqual(maker_amount, order_id['fee'], msg='maker开仓手续费不一致')
                            elif bid_uid1['is_taker'] == 1:
                                taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'maker_fee_ratio']
                                self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                            elif bid_uid1['is_taker'] == None:
                                print('用户不是aker')
                        else:
                            print("有可能用户不是maker")

                        # bid_order_id
                        if bid_uid != None:
                            if bid_uid['is_taker'] == -1:
                                maker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'maker_fee_ratio']
                                self.assertEqual(maker_amount, order_id['fee'], msg='maker开仓手续费不一致')
                            elif bid_uid['is_taker'] == 1:
                                taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'taker_fee_ratio']
                                self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                        else:
                            print("有可能用户不是taker")
                        '''
                        计算强平价
                    '''
                        print('方向', order_id['bs_flag'])
                        if order_id['bs_flag'] == 2:
                            # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)-追加保证金/合约数量+扣减保证金/合约数量
                            duocang = order_id['open_price'] * (1 - 1 / order_id['lever'] + maintenance)
                            print("多仓强平价格", duocang)

                            self.assertEqual(slice_Character.split_to(duocang), slice_Character.split_to(order_id['force_price']), msg='多仓强平价格不一致')

                        elif order_id['bs_flag'] == 1:
                            # 空仓强平价格 = 开仓价格* (1+起始保证金率-维持保证金率)+追加保证金/合约数量-扣减保证金/合约数量
                            kongcang = order_id['open_price'] * (1 + 1 / order_id['lever'] - maintenance)
                            print("空仓强平价格", kongcang)
                            print('数据库空仓强平价格', order_id['force_price'])
                            self.assertEqual(slice_Character.split_to(kongcang),
                                             slice_Character.split_to(order_id['force_price']), msg='空仓强平价格不一致')
                        '''
                       维持保证金 = 合约数量*开仓价格*维持保证金率
                                      '''
                        # weichi = quantity * price * maintenance
                        # print(weichi)

                        # 计算维持保证金
                        weichi = (order_id['open_price'] * order_id[
                            'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率

                        self.assertEqual(weichi, order_id['insurance_fund'], msg='维持保证金不一致')
                        print(weichi, order_id['insurance_fund'])
                    elif order_status1 == 3:
                        LOG.info('用户部分成交成功')
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

                        # 判断起始保证金
                        print('数据库起始保证金', order_id['amount'])
                        self.assertEqual(slice_Character.split_Four(baozhengjin),
                                         slice_Character.split_Four(order_id['amount']), msg='起始保证金数据不一致')
                        # 判断杠杆
                        self.assertEqual(s, order_id['lever'], msg='杠杆不一致')
                        '''
                        开仓手续费
                        '''
                        sql_pc_match = "select * from pc_match where bid_order_id in ('%s');" % (
                            wei_order_id)  # 根据订单id查询订单表
                        sql_pc_match1 = "select * from pc_match where ask_order_id in ('%s');" % (wei_order_id)
                        print(sql_pc_match)
                        bid_uid = db_link.get_one(sql_pc_match)
                        bid_uid1 = db_link.get_one(sql_pc_match1)

                        if bid_uid1 != None:
                            if bid_uid1['is_taker'] == -1:
                                maker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'taker_fee_ratio']
                                self.assertEqual(maker_amount, order_id['fee'], msg='maker开仓手续费不一致')
                            elif bid_uid1['is_taker'] == 1:
                                taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'maker_fee_ratio']
                                self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                            elif bid_uid1['is_taker'] == None:
                                print('用户不是aker')
                        else:
                            print("有可能用户不是maker")

                        # bid_order_id
                        if bid_uid != None:
                            if bid_uid['is_taker'] == -1:
                                maker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'maker_fee_ratio']
                                self.assertEqual(maker_amount, order_id['fee'], msg='maker开仓手续费不一致')
                            elif bid_uid['is_taker'] == 1:
                                taker_amount = order_id['open_price'] * order_id['contract_qty'] * symbol_BTC[
                                    'taker_fee_ratio']
                                self.assertEqual(taker_amount, order_id['fee'], msg='taker开仓手续费不一致')
                        else:
                            print("有可能用户不是taker")
                        '''
                        计算强平价
                    '''
                        print('方向', order_id['bs_flag'])
                        if order_id['bs_flag'] == 2:
                            # 多仓强平价格 = 开仓价格*(1-起始保证金率+维持保证金率)-追加保证金/合约数量+扣减保证金/合约数量
                            duocang = order_id['open_price'] * (1 - 1 / order_id['lever'] + maintenance)
                            print("多仓强平价格", duocang)

                            self.assertEqual(slice_Character.split_to(duocang), slice_Character.split_to(order_id['force_price']), msg='多仓强平价格不一致')

                        elif order_id['bs_flag'] == 1:
                            # 空仓强平价格 = 开仓价格* (1+起始保证金率-维持保证金率)+追加保证金/合约数量-扣减保证金/合约数量
                            kongcang = order_id['open_price'] * (1 + 1 / order_id['lever'] - maintenance)
                            print("空仓强平价格", kongcang)
                            print('数据库空仓强平价格', order_id['force_price'])
                            self.assertEqual(slice_Character.split_to(kongcang),
                                             slice_Character.split_to(order_id['force_price']), msg='空仓强平价格不一致')
                        '''
                       维持保证金 = 合约数量*开仓价格*维持保证金率
                        '''
                        # weichi = quantity * price * maintenance
                        # print(weichi)

                        # 计算维持保证金
                        weichi = (order_id['open_price'] * order_id[
                            'contract_qty']) * maintenance  # 取出taken手续费计算开仓保证金.开仓价格*数量*起始保证金率

                        self.assertEqual(weichi, order_id['insurance_fund'], msg='维持保证金不一致')
                        print(weichi, order_id['insurance_fund'])
                    else:
                        print('用户交易异常')
            elif retMsg=='委托失败' or retMsg=='杠杆不合法' or retMsg=='挂单量已达上限':
                #查询出用户pc_trade_order表中有几条数据，如果不满四条数据，说明用户不是因为挂单超数
                sql_pc_trade_order = "SELECT * FROM `pc_trade_order` WHERE uid='%s'" % (rise)  # 根据订单id查询订单表
                print(sql_pc_trade_order)
                sel_trade_order = db_link.get_all(sql_pc_trade_order)
                #说明用户有四条数据
                print(type(sql_pc_trade_order))
                print('数据的长度',len(sel_trade_order))
                if len(sel_trade_order)==4:
                    sql_pc_order = "SELECT * FROM `pc_order` WHERE uid='%s'" % (rise)  # 根据订单id查询订单表
                    print(sql_pc_order)
                    print(type(sql_pc_order))
                    sel_order = db_link.get_one(sql_pc_order)
                    print(type(sel_order))
                    print('查询用户所有交易单的状态',sel_order)
                    for order_in in range(1,len(sel_order)):
                        print(sel_order[order_in]['order_status'])
                        if sel_order[order_in]['order_status']==4:
                            print('用户已经有持仓的单子，不可以撤单只能平仓')
                        elif sel_order[order_in]['order_status']==3:
                            print('用户只可以部分撤单')
                            # if   判断用户先撤单，然后再次平仓，用户再次下单
                            #无法满足另外一种场景，部分平仓，只能再写方法，
                            #如何写判断用户加减杠杠 ，加减保证金额。在重新新建方法么
                        elif sel_order[order_in]['order_status']==2:
                            print('用户可以全部撤单')
                elif len(sel_trade_order)>3:
                    print("返回用户结果",retMsg)


if __name__ == '__main__':
    unittest.main()
