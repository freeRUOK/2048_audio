# --*-- Encoding: UTF-8 --*--
#! fileName: game.py
# * 2651688427@qq.com

# 2048游戏核心实现

import hashlib
import time
import random
from pygame import locals

# 游戏状态
STATUS_GAME_RUN = 0
STATUS_GAME_OVER = 1
STATUS_GAME_MERGE = 2
STATUS_GAME_OK = 3
STATUS_GAME_STOP = 4
STATUS_GAME_BACK = 5
STATUS_GAME_RECOVER = 6

# 四个方向
DIRECTION_UP = locals.K_UP
DIRECTION_DOWN = locals.K_DOWN
DIRECTION_LEFT = locals.K_LEFT
DIRECTION_RIGHT = locals.K_RIGHT


# 时间单位定义
time_seconds = 1
time_minutes = 60
time_hour = time_minutes * time_minutes
time_today = time_hour * 24

# 2048实现
class Game:
  # 初始化2048游戏
  def __init__(self):
    self.__handler = None # 游戏内部事件的处理函数
    self.__dataBack = {}
    self.__map = [0 for i in range(16)] # 创建空的4*4的方格
    self.__maxNumber = 64 # 初始最高分
    self.__playName = None
    self.__playHash = None
    self.__score = 0
    self.__numberCount = 0 # 方格里的有效数字的个数
    self.__time = 0 # 初始时间戳
    self.__len = 4 # 正方格的边长
    self.__random = random.Random() # 初始化随机数


  # 启动游戏
  def start(self):
    # 如果时间戳是0， 就获取当前系统的时间戳， 之后在方格里随机生成两个有效的数字
    if self.__time == 0:
      self.__time = int(time.time())
      self.__randomNumber()
      self.__randomNumber()

    self.__republicEvent(STATUS_GAME_RUN) #发布启动事件


  # 停止游戏,
  def stop(self, status = STATUS_GAME_STOP):
    self.__republicEvent(status) # 发布停止事件


  # 绑定游戏事件处理函数
  def bindEventHandler(self, handler):
    if handler:
      self.__handler = handler


  def unbindEventHandler(self):
    self.__handler = None


  # 发布游戏事件
  def __republicEvent(self, eventArgs = None):
    if self.__handler:
      self.__handler(eventArgs) # 调用游戏事件处理函数


  def back(self):
    self.__dataBack = {"map": [i for i in self.__map],
      "maxNumber": self.__maxNumber, 
      "score": self.__score, 
      "numberCount": self.__numberCount, 
      }
    self.__republicEvent(STATUS_GAME_BACK)


  def recover(self):
    if len(self.__dataBack) != 0:
      self.__map = [i for i in self.__dataBack["map"]]
      self.__maxNumber = self.__dataBack["maxNumber"]
      self.__score = self.__dataBack["score"]
      self.__numberCount = self.__dataBack["numberCount"]
      self.__republicEvent(STATUS_GAME_RECOVER)


  # 方格上生成有效的随机数字
  def __randomNumber(self):
    if self.__numberCount >= len(self.__map): # 如果有效数字填满整个方格的话直接返回
      return

    # 在方格里确定一个没有占用的位置
    index = self.__random.randint(0, len(self.__map) - 1)
    while self.__map[index] != 0:
      index = self.__random.randint(0, len(self.__map) - 1)

    # 确定数字2或者4出现的概率
    if self.__random.randint(0, 8) > 7:
      value = 4
    else:
      value = 2

    self.__map[index] = value # 在确定的位置上生成确定的数字
    self.__numberCount += 1 # 有效数字多了一个


  # 返回方格某个位置上的数字
  def pointer(self, value):
    if value >= 0 and value < len(self.__map):
      return self.__map[value]
    else:
      raise ValueError("Input Pointer Error.")


  # 返回玩家昵称
  def getName(self):
    return self.__playName


  # 返回玩家hash值
  def getHash(self):
    return self.__playHash


  # 返回玩家当前游戏分数
  def getScore(self):
    return self.__score


  # 返回玩家本局游戏持续时间(秒钟）
  def getTime(self):
    return int(time.time()) - self.__time


  # 返回玩家信息
  def getInfo(self):
    return {
      "name": self.getName(), 
      "hash": self.getHash(), 
      "score": self.getScore(), 
      "time": self.getTime()
      }

  # 在一个方向移动所有的数字
  def merge(self, direction):
    if direction == DIRECTION_RIGHT or direction == DIRECTION_DOWN:
      start = 0
      stop = len(self.__map)
      step = 5
    else:
      start = len(self.__map) - 1
      stop = -1
      step = -5

    for i in range(start, stop, step):
      indexs = self.pointers(i, direction)
      i = 0
      while i + 1 < len(indexs):
        result = self.mergeOne(indexs[i], indexs[i + 1])
        if i + result > -1:
          i += result

    self.__randomNumber()
    self.__randomNumber()

    status = STATUS_GAME_RUN
    if self.__isGameOk():
      status = STATUS_GAME_OK

    self.__republicEvent(status)

    if self.__isGameOver():
      self.stop(STATUS_GAME_OVER)


  # 获取某个方向的所有索引
  def pointers(self, p, direction):
    w = self.__len
    l = len(self.__map)
    pointers = None
    if direction == DIRECTION_UP or direction == DIRECTION_DOWN:
      pointers = [i for i in range(p % w, l, 4)]
    else:
      p = p // w * w

      pointers = [i for i in range(p, p + w)]

    if direction == DIRECTION_UP or direction == DIRECTION_LEFT:
      pointers.reverse()

    return pointers


  # 根据合并的情况修改游戏状态
  def mergeOne(self, x, y):
    map = self.__map
    if map[x] == 0 and map[y] == 0:
      return 2
    elif map[x] == 0 and map[y] != 0 or map[x] != 0 and map[y] != 0 and map[x] != map[y]:
      return 1
    elif  map[x] != 0 and map[y] == 0:
      map[x], map[y] = map[y], map[x]
      return -1
    else:
      map[y] += map[x]
      map[x] = 0
      self.__numberCount -= 1
      self.__setScore()
      self.__republicEvent(STATUS_GAME_MERGE)
      return -1


  # 游戏是否成功
  def __isGameOk(self):
    maxValue = max(self.__map)
    if maxValue >= self.__maxNumber:
      self.__maxNumber = maxValue * 2
      return True

    return False


  # 游戏是否失败
  def __isGameOver(self):
    if self.__numberCount < len(self.__map):
      return False

    for i in range(0, len(self.__map), self.__len + 1):
      leftIndexs = self.pointers(i, DIRECTION_LEFT)
      downIndexs = self.pointers(i, DIRECTION_DOWN)
      x, y = 0, 0
      while x < len(leftIndexs) - 1 or y < len(downIndexs) - 1:
        if self.__map[leftIndexs[x]] == self.__map[leftIndexs[x + 1]] or self.__map[downIndexs[y]] == self.__map[downIndexs[y + 1]]:
          return False

        x, y = x + 1, y + 1

    return True


  # 返回游戏状态描述
  def description(self):
    gameTime = (int(time.time()) - self.__time)
    fmt = "得分： {}, 用时".format(self.__score)
    for t in [time_today, time_hour, time_minutes, time_seconds]:
      a = gameTime // t
      gameTime %= t
      if a != 0:
        fmt = "{}:{:02}".format(fmt, a)

    return fmt


  # 设置游戏分数
  def __setScore(self):
    s = sum(self.__map)
    x = s * max(self.__map)
    self.__score = x


  # 设置游戏玩家昵称
  def setName(self, name):
    if self.__playHash:
      self.__playName = name


  # 设置或者更新玩家hash， 如果需要更新hash需要提供原hash
  def setHash(self, newHash, oldHash=None):
    if self.__playHash is None:
      self.__playHash = newHash
    elif oldHash:
      self.__playHash = newHash
