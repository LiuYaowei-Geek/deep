import unittest
from Interface.test_login import Test_Login
from Public.log import LOG
from Public.read_excel import read_excel
from Public.cogfig import EXECL_PATH
from Public.db_commit import db_commit #数据库
import ddt
import requests
import time
from Interface.tese_requests_single import requests_single
wenjian = EXECL_PATH + '\\creata_interface.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian, '下单接口测试')
db_link=db_commit()

url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
rise='315655'

'''
下单异常测试
'''
@ddt.ddt()
class create_order(unittest.TestCase):
    def setUp(self):
        LOG.info('下单接口测试结束')
    def tearDown(self):

        LOG.info('下单接口测试结束')

    @ddt.data(*excel.next())
    def test_create(self,data):
        test = Test_Login(rise)
        token_test = test.test_log()
        '''
        计算强评价
        维持保证金
        注意：取参数时，需要查看execl是否有多余的空格
        :param data:
        :return:
        '''
        quantity = float(data['quantity(数量)'])
        lever = float(data['lever(杠杆)'])
        bs_flag = int(data['bs_flag(1买跌/2买涨)'])
        price = data['price(限价单)']
        order_type = int(data['order_type(订单类型1市场 2限价)'])
        contract_id = data['contract_id(交易对)']
        paramt_type = data['期望请求方式']
        print(lever)
        # 1、市场价买涨算强平价格计算
        # 2、多仓强平价格 = 开仓价格 * (1 - 起始保证金率 + 维持保证金率)
        # 查询维持保证金率
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = float(maintenance_margin['maintenance_margin_rate'])  # 取出维持保证金率
        # #起始保证金率(1 - 1 / lever-维持保证金率)
        # Strong_parity = price * (1 - 1 / lever - maintenance)
        # print('强平价', Strong_parity)

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

            api_json = api.getJson()  # 取返回joson值里面的值
            retMsg = api_json.get('retMsg')
            try:
                self.assertEqual(retMsg, '委托下单成功', msg='下单失败')
            except Exception as e:
                print(e)
            plan_order_id1 = api_json.get('retData').get('plan_order_id')  # 取出订单id
            sql_plan_order_id = "SELECT * FROM `pc_order` WHERE order_id='%s'" % (plan_order_id1)  # 根据订单id查询订单表
            print(sql_plan_order_id)

            plan_order = db_link.get_one(sql_plan_order_id)

            print('查询订单', plan_order)
            '''
                                              计算execl和落库的数据是否一致
            '''

            try:
                s1_list = str(price).split('.')
                s1_new = s1_list[0] + '.' + s1_list[1][:2]
                self.assertEqual(s1_new, str(plan_order['price']).rstrip('0').strip('.'),
                                 msg='参数1下单价格跟数据库价格不一致')
                self.assertEqual(lever, str(plan_order['lever']).rstrip('0').strip('.'),
                                 msg='下单杠杆跟数据库价格不一致')
                self.assertEqual(int(bs_flag), plan_order['bs_flag'], msg='下单方向跟数据库价格不一致')
                self.assertEqual(int(order_type), plan_order['order_type'],
                                 msg='下单订单类型跟数据库价格不一致')
                self.assertEqual(round(amount, 4), float(plan_order['amount']), msg='保证金不相等')
            except Exception as e:
                print(e)


            print(type(quantity), type(price), type(lever))
            '''
            计算起始保证金是否相等
            '''
            try:
                amount = quantity * float(price) / lever  # 计算起始保证金
            except Exception as e:
                print(e)
            try:
                self.assertEqual(round(amount, 4), float(plan_order['amount']),
                                 msg='保证金不相等')  # 取出数据库的保证金，数据库中的保证金对比是否相等，如果有异常包住，继续
            except Exception as e:
                print(e)

            symbol = "SELECT * FROM `pc_contract` WHERE symbol='BTC/USDT'"  # 计算预收开仓手续费，用taker来计算的
            print(symbol)
            symbol_BTC = db_link.get_one(symbol)
            try:
                taker_fee_ratio = quantity * price * float(symbol_BTC['taker_fee_ratio'])  # 取出开仓手续费计算开仓保证金.开仓价格*数量*起始保证金率
                # 判断开仓手续费是否相等
                str(plan_order['lever']).rstrip('0').strip('.')
                self.assertEqual(taker_fee_ratio, str(plan_order['open_fee']).rstrip('0').strip('.'))
                # 判断平仓手续费是否相等
                self.assertEqual(taker_fee_ratio,str(plan_order['close_fee']).rstrip('0').strip('.'))
                # 判断杠杆是否相等
                self.assertEqual(lever, str(plan_order['lever']).rstrip('0').strip('.'))
                Balance = amount + taker_fee_ratio * 2
                sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type='get',
                                                   paramt=paramt, headers=i)
                usdt_Balance = sql_usdt_Balance.getJson()
                keyong = usdt_Balance.get('retData').get('futures_usdt_balance')
                print('keyong', keyong)
                shengyu = float(totoal) - float(keyong)
                print(float(totoal) - float(keyong))
                print("剩余余额", shengyu)
            except Exception as e:
                print(e)
            try:
                self.assertEqual(shengyu, Balance, msg='扣减额度不正确')
            except Exception as e:
                print(e)
if __name__ == '__main__':
    unittest.main()
