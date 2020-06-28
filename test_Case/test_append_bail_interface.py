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
wenjian = EXECL_PATH + '\\append_bail.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian, '调整保证金')
db_link=db_commit()

url = 'https://t01-mapi.deepcoin.pro/site/kill'
headers_1= {"Content-Type": "application/json", }
api_kill= requests.get(url=url,headers=headers_1)
time.sleep(3)
rise='316173'

'''
撤单接口异常测试
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
        trade_order_id = data['trade_order_id']
        bail_amount = data['bail_amount']
        side = data['side']
        is_append_bail = data['is_append_bail']
        paramt_type = data['期望请求方式']
        # 1、市场价买涨算强平价格计算
        # 2、多仓强平价格 = 开仓价格 * (1 - 起始保证金率 + 维持保证金率)
        # 查询维持保证金率
        sql = ('SELECT * FROM pc_risk_limit')
        maintenance_margin = db_link.get_one(sql)  # 查询维持保证金率第一条数据
        maintenance = float(maintenance_margin['maintenance_margin_rate'])  # 取出维持保证金率
        # #起始保证金率(1 - 1 / lever-维持保证金率)
        # Strong_parity = price * (1 - 1 / lever - maintenance)
        # print('强平价', Strong_parity)

        paramt = {'trade_order_id': trade_order_id,'bail_amount':bail_amount,'side':side,'is_append_bail':is_append_bail}  # 拼接参数
        print(paramt)
        for i in token_test['token']:  # 循环里面token_test的值
            sql_usdt_Balance = requests_single(url='https://t01-mapi.deepcoin.pro/pc/balance', requersts_type=paramt_type,
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

if __name__ == '__main__':
    unittest.main()
