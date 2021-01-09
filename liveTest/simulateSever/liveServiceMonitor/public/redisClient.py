#!/usr/bin/python3
# coding=utf-8
from redis import Redis
from rediscluster import RedisCluster

class RedisClient:
    def __init__(self, host,port):
        self.host = host
        self.port = port
        # self.password = password
        # redis.StrictRedis(host=db_host, port=db_port,decode_responses=True)
        #self.conn = Redis(self.host, self.port, socket_connect_timeout=3, socket_timeout=3)
        redis_nodes = [{'host': '10.200.2.220', 'port': 6381},
                       {'host': '10.200.2.220', 'port': 6383},
                       {'host': '10.200.2.220', 'port': 6385}
                       ]
        try:
            self.conn = RedisCluster(startup_nodes=redis_nodes)
        except Exception as e:
            print("Connect Error!", e)


    def set(self, name, value, expire=None):
        self.conn.set(name, value, expire)

    def hset(self, name, key, value):
        self.conn.hset(name,key, value)

    def get(self, name):
        return self.conn.get(name)

    def delete(self, name):
        self.conn.delete(name)

    def setex(self, name, value, time):
        self.conn.setex(name, value, time)

    # 同时将多个 field-value (字段-值)对设置到哈希表中
    def hm_set(self, name, value):
        self.conn.hmset(name, value)

    # 用于返回哈希表中，一个或多个给定字段的值
    def hm_get(self, name):
        return self.conn.hgetall(name)

    def hm_delete(self, name):
        self.conn.hdel(name)


# if __name__ =='__main__':
#     redis=RedisClient('127.0.0.1','6385','0')
#     redis.set('live_id','1122')
#     token = redis.get('live_id')
#     # token=redis.get('peng')
#     print(token)