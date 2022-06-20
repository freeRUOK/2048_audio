# --*-- Encoding: UTF-8 --*--
#! filename: data_manager.py
# * 2651688427@qq.com

# 操作mongoDB数据库
import hashlib
import random
import time

import redis

ERROR_OK = 1
ERROR_FAIL = 0
PLAY_SET = "play_set"

# 操作数据
class Top:
  def __init__(self):
    self.__pool = redis.ConnectionPool(host="localhost", port=6379, decode_responses=True)


  # 初始化一个新hash
  def initPlay(self):
    md5 = hashlib.md5()
    md5.update("{}{}".format(str(time.time()), str(random.randint(0, 9999999))).encode())
    connection = redis.Redis(connection_pool = self.__pool)
    hash = md5.hexdigest()
    if connection.sadd(PLAY_SET, hash):
      return hash


  # 返回全部数据
  def getAll(self):
    results = []
    connection = redis.Redis(connection_pool=self.__pool)
    for key in connection.sscan_iter(PLAY_SET):
      if connection.exists(key):
        results.append(connection.get(key))

    return results


  # 更新一个数据
  def updatePlay(self, key, data):
    connection = redis.Redis(connection_pool=self.__pool)
    if connection.sismember(PLAY_SET, key) and connection.set(key, data):
      return ERROR_OK
    else:
      return ERROR_FAIL
