from unittest import mock


def need_mock():
    a = 1
    b = 2
    ## 假设他的实际返回值为a+b
    return a + b


def use_mock_func():
    ## 使用mock的函数
    print(need_mock())


## 这里mock对应函数
need_mock = mock.Mock(return_value='123')

## 调用测试一下
use_mock_func()