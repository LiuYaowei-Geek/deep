import redis   # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库

class redis_dta:
    def redis_value(self,rs_value):
        r = redis.Redis(host='103.14.33.145', port=6379, db=0)   # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379>>> import redis
        # value=r.hget('order_book', 'match_BTCUSDT')
        r.hset("price", "mark_BTCUSDT", rs_value)
        print(r.hget("price", "mark_BTCUSDT"))  # 单个取hash的key对应的值
        # return value


