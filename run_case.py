import unittest,os,time
from Public import HTMLTestRunner
from Public.log import LOG,logger

if __name__=='__main__':
    atestsuite=unittest.defaultTestLoader.discover('test_Case',pattern='test_*.py')#自动查找指定文件夹下，以test_开头的.py模块里面的每一个测试方法

    now = time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))#获取当前时间
    # 获取项目包的目录
    basedir=os.path.dirname(os.path.abspath(__file__))
    #查询到test_Report包的目录
    file_dir=os.path.join(basedir,'test_Report')

    print("包的路径",file_dir)
    #定义文件名
    file_name=os.path.join(file_dir,(now+'.html'))
    #创测试报告的html文件，此时还是个空文件
    fb=open(file_name,'wb')
    print(LOG.info('1111'))
    #打开测试报告
    runner = HTMLTestRunner.HTMLTestRunner(stream=fb, title='BBJ接口测试报告', description='BBJ接口测试结果')
    #运行测试容器中的用例，并将结果写入的报告中
    runner.run(atestsuite)



