import requests
import json
class requests_login_packge(object):
    '''
    适合execk多个参数循环的，配read_execl方法
    '''
    def __init__(self,url,requersts_type,mobile,code):
        self.url=url
        self.requersts_type=requersts_type
        self.mobile=mobile
        self.code=code
    def test_login_api(self):
        paramt={'mobile':self.mobile,'code':self.code}
        if self.requersts_type=="post" :
            response=requests.post(self.url,data=paramt)
        elif self.requersts_type=="get":
            response=requests.get(self.url)
        return response

    def getJson(self):
        json_data = self.test_login_api()
        return json.loads(json_data.text)