from Public.log import logger,LOG
import os
import requests
import json
import ddt
import unittest
from Public.read_excel import read_excel
from Public.db_commit import db_commit
from Public.cogfig import EXECL_PATH
from Interface.test_requests_pk import requests_packge
wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'Sheet3')

@ddt.ddt()
class Test_Login(unittest.TestCase):
    def setUp(self):
        logger("运行")
    def tearDown(self):
       pass
    @ddt.data(*excel.next())
    def test_shuj(self,data):
        print(data)
        api=requests_packge(url=data['url'],requersts_type=data['期望请求方式'],mobile=int(data['quantity']),code=int(data['lever']),bs_flag=data['bs_flag'])
        api.getJson().get('retMsg')




if __name__ == '__main__':
    unittest.main()

