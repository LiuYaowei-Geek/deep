from Public.log import logger,LOG
import os
import requests
import json
import ddt
import unittest
from Public.read_excel import read_excel
from Public.db_commit import db_commit
from Public.cogfig import EXECL_PATH
wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
excel = read_excel(wenjian,'Sheet2')
@ddt.ddt()
class Test_Login(unittest.TestCase):
    def setUp(self):
        logger("运行")
    def tearDown(self):
       pass
    @ddt.data(*excel.next())
    def test_shuj(self,data):
        s=int(data['mobile'])
        code=int(data['code'])

        r={'mobile':s,'code':code}

        params2=r

        url=data['url']
        f = requests.post(url, data=params2)
        h=json.loads(f.text).get('retMsg')
        print(h)
        try:
            self.assertEqual(h,'登录成功',msg='登录成功')
        except Exception as e:
            print('异常',e)







if __name__ == '__main__':
    unittest.main()

