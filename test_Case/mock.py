import unittest
import time
import ddt
import json
from Public.cogfig import EXECL_PATH
from Interface.test_mock import test_mock_mi
test_send = test_mock_mi()
import math
from Public.read_excel import read_excel
from unittest import mock
wenjian = EXECL_PATH + '\\jekn.xlsx'  #查询到对应的case文件
index_excel = read_excel(wenjian, '指数价')
#上一次指数价
last_prices=9409.9
@ddt.ddt()
class TestClient(unittest.TestCase):
    def test_fail_request(self,test):
    #     #调用方法实例化，f获得test_send的实例
    #     f=test_send.test_send_requestr()
    #     #把返回值作为mock，mock
    #     f=mock.Mock(return_value='404')
    #     #调用属性实例化
    #     print(type(f))
    #     self.assertEqual(f(), '404')
    #指数价

        #统计
        sum = 0
        #金额不为0的用户，保存进入prices
        prices = []
        for i in range(len(test)):
            if float(test[i]) > 0:
                sum += float(test[i])
                prices.append(test[i])
        num = len(prices)
        #记录prices的总长度等于0直接返回0
        if num == 0:
            return 0
        ##记录prices的总长度等于1
        elif num == 1:
            global last_prices
            # 计算当前价格-上一次的价格/上一次的价格是否大于0.25
            if math.fabs(float(prices[0]) - float(last_prices)) / float(last_prices) > 0.25:
                # 直接返回上一次的价格，因为跑出来的指数价格跟上一次的指数价格差距太大
                return last_prices
            else:
                # 返回当前的指数价格
                prices[0]
        ##记录prices的总长度等于2
        elif num == 2:
            #计算prices的第一个数值减去第二个数组
            dp = float(prices[0]) - float(prices[1])
            #计算出来的第一个数值减去第二个数组的总值是否小于0
            if dp <= 0: #dp小于0是正常的
                #1、把总值转成整数
                #2、判断总值/价格1>0.25
                if -dp / float(prices[0]) > 0.25: #如果值大于0.25就是异常
                    #价格1-上一次价格<=价格2-上一次价格
                    if math.fabs(float(prices[0]) - last_prices) <= math.fabs(float(prices[1]) - last_prices):
                        print(prices[0])
                        #直接返回价格1
                        return prices[0]
                    else:
                        #返回价格2
                        return prices[1]
                else:
                    #总的价格/平均价
                    index = sum / float(num)
                    print("指数价", index)
                    last_prices= index
                    return index
            else:
                #
                if dp / float(prices[1]) > 0.25:
                    if math.fabs(prices[0] - last_prices) <= math.fabs(prices[1] - last_prices):
                        return prices[0]
                    else:
                        return prices[1]
                else:
                    return sum / float(num)
        #数组里面有三个价格
        avg = sum / float(num)
        #记录异常的价格
        nums = 0
        for i in range(len(prices)):
            dv = math.fabs((float(prices[i]) - avg) / avg)
            print(dv)
            if dv > 0.03:
                nums += 1
                prices[i] = 0

        if nums == 0:
            print(nums)
            return avg
        return self.test_fail_request(prices)

    # #正常的数值
    # def test_1_average_value(self):
    #     s=1
    #     while True:
    #         if s <= 1:
    #             test = test_send.test_send_requestr()
    #             # if r_binance
    #             print(test)
    #
    #             price = self.test_fail_request(test)
    #             print('指数值', price)
    #             if price > 0:
    #                 last_prices = price
    #             time.sleep(0.5)
    #             s += 1
    #         else:
    #             break

    #指标表价只有一个值
    @ddt.data(*index_excel.next())
    def test_2_to_value(self,data):
        s=1
        test_list = data['指数价']
        while True:
            if s <= 1:
                test = test_send.test_send_requestr()
                print("分割", type(test_list))
                last_list=test_list.split(',')
                print("分割",type(last_list))
                price_list=[]

                #计算取出来的值，若取出来的值偏差大于0.25，就返回上一次的指数价
                for i in range(0,len(last_list)):
                    global last_prices
                    f=math.fabs(float(last_prices) - float(last_list[i])) / float(last_prices)
                    print(f)

                    if f> 0.25:

                        price_list.append(0)
                    else:
                        #last_prices = last_list[i]
                        price_list.append(last_list[i])
                test = mock.Mock(return_value=price_list)
                #     #调用属性实例化

                test_list=test()

                price = self.test_fail_request(test_list)
                print('指数值',price)
                time.sleep(0.5)
                if float(price)>0:
                    last_prices = price
                s += 1
            else:
                break

if __name__ == '__main__':
    unittest.main()
