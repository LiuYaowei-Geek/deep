from Public.log import logger,LOG
import os
import requests
import json
import ddt
import unittest
from Public.get_execl import read_excel
from Public.db_commit import db_commit
from Public.cogfig import EXECL_PATH
wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'Sheet1')
db_link=db_commit()
mysql_link=db_link.connect()
'''
不用数据驱动取单个值
'''
class Test_Login(unittest.TestCase):
    def setUp(self):
        logger("运行")
    def tearDown(self):
       pass
    def test_shuj(self):
        #获取execl里面的第一列
        data1 = excel.exexl('url')
        #获取exexl的第二列参数值
        data2 = excel.exexl('参数')

        #取出第一列的参数值的第二个
        host =data1[0]["url"]
        #【参数】头，取出第二列，列表是已下标为索引
        w1=data2[1]['参数']
        print('参数',w1)
        #把str转成字典
        user_dict = eval(w1)
        print('*' * 50)
        #取出第二个列的mobile
        print(user_dict['mobile'])

        params=eval(data2[0]['参数'])
        r = requests.post(host,data=params)
        print('text',r.url)
        try:
            token=json.loads(r.text).get('retData').get('token')
            print(token)
        except Exception as e:
            self.assertEqual(token, 'None', msg='token为空')
        finally:
            host1 = data1[1]["url"]

            headers = {"Content-Type": "application/x-www-form-urlencoded", "token": token}
            print(headers)

        params2 = eval(data2[1]['参数'])
        print("第二个URL的参数",type(params2))
        f=requests.post("https://t01-mapi.deepcoin.pro/pc/create-order",data=params2,headers=headers )
        print('下单',f.url)
        regMsg=json.loads(f.text).get('retMsg')
        print(f.json())


        sql='SELECT * from  otc_orders ORDER BY timestamp DESC'
        sql_order_by=db_link.get_one(sql)
        print(sql_order_by)
        try:
            self.assertEqual(sql_order_by[0],regMsg,msg='不相等')
        except Exception as e:
            print(e)

        return r
if __name__ == '__main__':
    unittest.main()
