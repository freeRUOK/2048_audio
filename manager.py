# --*-- Encoding: UTF-8 --*--
#! fileName: manager.py
# * 2651688427@qq.com
# 实现游戏的管理逻辑， 包括和核心游戏交互， 用户界面管理等等

import json
import hashlib
import os
import sys
import time
import pickle
import re
from functools import cmp_to_key
# 如下依赖包需要安装
import requests
import pygame
import pygame.mixer
from pygame.locals import *
import wx
# 如下依赖包是本程序的其他部分
from game import *
from tts import *

# 音效目录
SOUND_DIR = os.path.join(os.getcwd(), "sounds\\")
# 背景音乐路径
BACKGROUND_DIR = SOUND_DIR + "background.mp3"
# 配置文件路径
SETTING_PATH = os.path.join(os.getcwd(), "setting.json")
# 核心游戏发送的星号常量和管理器的控制常量
begin = "begin"
ok = "ok"
over = "over"
quit = "quit"
merge = "merge"
move = "move"
error_pointer = "error_pointer"
pointer = "pointer"
back = "back"
recover = "recover"
restart = "restart"
immovable = "immovable"

# 主要管理器
class Manager:
  def __init__(self):
    pygame.init()
    self.__tts = self.__get_tts()

    self.__gamePath = os.path.join(os.getcwd(), "game.dat")
    self.__serviceSetting = self.__loadService()
    self.__game = self.load()
    self.__game.start()
    self.__display = pygame.display.set_mode((300, 300), 10, 10)
    pygame.display.set_caption("2048")
    # 2048的16个位置和键盘上的按键映射
    self.__inputs = [K_1, K_2, K_3, K_4, 
      K_q, K_w, K_e, K_r, 
      K_a, K_s, K_d, K_f, 
      K_z, K_x, K_c, K_v, 
      K_UP, K_DOWN, K_LEFT, K_RIGHT]
    pygame.mixer.init()
    self.__sounds = self.__load_sound()


  # 还原缓存的游戏数据
  def load(self):
    if os.path.exists(self.__gamePath):
      fp = open(self.__gamePath, "rb")
      instance = pickle.load(fp)
      fp.close()
    else:
      instance = Game()
      if self.__serviceSetting:
        result = Util.download("http://{}:{}/do-init".format(self.__serviceSetting["host"], self.__serviceSetting["port"]))
        if result["error_code"] == 1:
          instance.setHash(result["hash"])
        else:
            self.__tts.Speak("获取服务器端身份令牌失败， 请确认服务器配置是否有误", True)

    instance.bindEventHandler(self.__gameEventHandler)
    return instance


  # 缓存游戏数据
  def save(self):
    self.__game.unbindEventHandler()
    fp = open(self.__gamePath, "wb")
    pickle.dump(self.__game, fp)
    fp.close()


  # 加载游戏音效和背景音乐
  def __load_sound(self):
    sounds = {}
    for name in os.listdir(SOUND_DIR):
      if os.path.isfile(SOUND_DIR + name) and name[-4: ].lower() == '.wav':
        sounds.update({name[ :-4]: pygame.mixer.Sound(SOUND_DIR + name)})

    return sounds


  # 获取tts引擎
  def __get_tts(self):
    engines = Engines()
    if not engines.isConfigure():
      engines.configure()

    return engines.getCurrentEngine()


  # 启动游戏
  def start(self):
    pygame.mixer.music.load(BACKGROUND_DIR)
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)
    self.__sounds[begin].play()
    # 进入游戏循环
    while True:
      for event in pygame.event.get():
        if event.type == KEYDOWN:
          # 分别调用应用控制函数和游戏控制函数
          if event.mod & KMOD_CTRL:
            self.__ctrl_app(event.key)
          else:
            self.__ctrl_game(event.key)

      pygame.event.pump()
      time.sleep(0.05)


  # 应用控制器
  def __ctrl_app(self, key):
    if key == K_e:
      self.__game.stop() # 停止游戏
    elif key == K_d:
      self.__tts.speak(self.__game.description(), True) # 朗读游戏状态
    elif key == K_r:
      self.__game.recover() # 回退上一个游戏状态
    elif key == K_b:
      self.__game.back() # 设定当前游戏状态可以按CTRL+r回退到这个状态， 只能设定一次
    elif key == K_c:
      wxApp = wx.App()
      if wx.MessageBox("您确实要放弃本轮游戏， 重新开始么？\n数据不可恢复！", caption="询问：", style=wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
        if os.path.exists(self.__gamePath):
          os.remove(self.__gamePath)

        self.__game = self.load()
        self.start()
        self.__tts.speak("新一轮游戏已经开始。", False)
      else:
        self.__tts.speak("游戏继续。", False)

      wxApp.Destroy()
    elif key == K_o:
      # 打开玩家排行榜列表， 需要配置一个服务器
      self.__showPlayTop()
    elif key == K_t:
      engines = Engines()
      engines.configure()
      self.__tts = Engines().getCurrentEngine()


  # 游戏控制器
  def __ctrl_game(self, key):
    try:
      index = self.__inputs.index(key) # 获取游戏输入所以
      if index >= 0 and index <= 15:
        # 朗读当前游戏坐标
        self.__sounds[pointer].play()
        currentPointer = self.__game.pointer(index)
        self.__tts.speak(str(currentPointer), True)
      elif index >= 16 and index <= 19:
        # 移动游戏上的数字， 
        self.__game.merge(self.__inputs[index])
      else:
        pass
    except ValueError:
      self.__sounds[error_pointer].play()

  # 处理游戏事件, 什么合并， 陈工， 失败， 根据这些采取相应的措施
  def __gameEventHandler(self, gameStatus):
    if gameStatus == STATUS_GAME_MERGE:
      self.__sounds[merge].play()
    elif gameStatus == STATUS_GAME_MOVE:
      self.__sounds[move].play()
    elif gameStatus == STATUS_GAME_OK:
      self.__sounds[ok].play()
    elif gameStatus == STATUS_GAME_OVER:
      self.__on_game_over()
    elif gameStatus == STATUS_GAME_STOP:
      self.__sounds[quit].play()
      self.__tts.speak("{}, 欢迎下次继续。".format(self.__game.description()), False)
      time.sleep(1)
      self.save()
      sys.exit()
    elif gameStatus == STATUS_GAME_BACK:
      self.__sounds[back].play()
    elif gameStatus == STATUS_GAME_RECOVER:
      self.__sounds[recover].play()
    elif gameStatus == STATUS_GAME_IMMOVABLE:
      self.__sounds[immovable].play()


  # GAME_OVER事件处理程序
  def __on_game_over(self):
    self.__sounds[over].play()
    time.sleep(1.8)
    if self.__game.isBack():
      self.__tts.speak("游戏失败， 即将回退！", False)
      self.__game.recover()

    else:
      self.__tts.speak("游戏失败， 即将重新开始， 本局游戏{}".format(self.__game.description()), False)
      if os.path.exists(self.__gamePath):
        os.remove(self.__gamePath)

      self.__game = self.load()
      self.__game.start()

    time.sleep(0.5)
    for i in range(10):
      self.__sounds[restart].play()
      time.sleep(0.3)


  # 打开玩家排行榜列表
  def __showPlayTop(self):
    if self.__serviceSetting is None:
      self.__tts.speak("没有可用的服务器, 具体参阅相关文档", True)
    else:
      GameDialog(game=self.__game, manager=self)


  # 加载服务器配置
  def __loadService(self):
    try:
      fp = open(SETTING_PATH)
      serviceSetting = json.load(fp)["setting"]["service"]
      fp.close()
    except:
      serviceSetting = None

    return serviceSetting


  # 获取服务器端配置信息
  def getServiceSetting(self):
    return self.__serviceSetting


  # 获取全部服务器端数据
  def serviceAll(self, params=None, callback=None):
    result = Util.download("http://{}:{}/do-all".format(self.__serviceSetting["host"], self.__serviceSetting["port"]), params=params)
    result = sorted(result, key = cmp_to_key(Util.cmp), reverse = True)
    if len(result) > 0 and callback:
      callback(result)


  # 更新当前玩家的数据到服务器端
  def serviceUpdate(self, data):
    result = Util.download("http://{}:{}/do-update".format(self.__serviceSetting["host"], self.__serviceSetting["port"]), method="POST", params=data)
    return result["error_code"]


  # 玩家排行榜用户界面
class GameDialog(wx.Dialog):
  def __init__(self, game=None, manager=None):
    self.__app = wx.App()
    wx.Dialog.__init__(self, None, title="2048玩家排行榜")
    self.__game = game
    self.__manager = manager
    self.__plays = None
    if game.getHash():
      name = game.getName()
      if name is None:
        self.nameLabel = wx.StaticText(self, label="昵称： （2到7个汉字）")
        self.nameText = wx.TextCtrl(self)
        self.nameBtn = wx.Button(self, label="确认提交(&S)")
      else:
        meInfo = "{}, {}分, {}".format(name, game.getScore(), Util.time2str(game.getTime()))
        self.nameLabel = wx.StaticText(self, label="我的状态")
        self.nameText = wx.TextCtrl(self, value=meInfo, style=wx.TE_READONLY)
        self.nameBtn = wx.Button(self, label="确认更新(&U)")

      self.nameBtn.Bind(wx.EVT_BUTTON, self.OnNameBtnClick)
    else:
      if manager.getServiceSetting():
        wx.MessageBox("您已经配置了服务器端， 如需使用请删除游戏数据。\n暂不支持原有数据直接使用……\n因此带来的不便深表歉意……", caption=="提示：")

    self.listBox = wx.ListBox(self)
    self.listBox.Bind(wx.EVT_SET_FOCUS, self.OnListBoxSetFocus)
    self.__manager.serviceAll(callback=self.__ShowTop)

    self.cancelBtn = wx.Button(self, id = wx.ID_CANCEL, label="关闭(&C)")
    self.ShowModal()


  # 在列表框上填充数据
  def __ShowTop(self, data):
    self.__plays = data
    fmts = []
    for index in range(len(self.__plays)):
      fmts.append("第{}名：{}, {}分, 用时{}".format(index + 1, self.__plays[index]["name"], self.__plays[index]["score"], Util.time2str(self.__plays[index]["time"])))

    self.listBox.Set(fmts)
    if self.__game.getName():
      self.nameLabel.SetLabel("我的状态：")
      info = self.__game.getInfo()
      self.nameText.SetValue("{}, {}分， {}".format(info["name"], info["score"], Util.time2str(info["time"])))
      self.nameBtn.SetLabel("更新(&U)")


  # 列表框获得焦点
  def OnListBoxSetFocus(self, event):
    if self.listBox.Size and self.listBox.Selection == -1:
      self.listBox.Selection = 0


  # 玩家昵称提交处理函数
  def OnNameBtnClick(self, event):
    data = self.__game.getInfo()
    if self.__game.getName() is None:
      newName, err = self.SetName(self.nameText.GetValue().strip())
      if err == 0:
        self.__game.setName(newName)
        data["name"] = newName
      elif err == 1:
        wx.MessageBox("昵称不合法， 需要2到7个汉字", caption="输入错误：", style=wx.ICON_ERROR)
      else:
        wx.MessageBox("该昵称已经被占用， 请换一个昵称。", caption="崇明：", style=wx.ICON_ERROR)

      if err != 0:
        self.nameText.SetFocus()
        return

    result = self.__manager.serviceUpdate(data)
    if result == 0:
      wx.MessageBox("更新数据失败。 请删除游戏数据《game.dat》文件\n具体问题和开发人员联系反馈——带来的不变敬请谅解……")
    else:
      self.__manager.serviceAll(callback=self.__ShowTop)


  # 设置一个合法的玩家昵称
  def SetName(self, name):
    m = re.match(r"[\u4e00-\u9fa5]{2,7}", name)
    if m and m.group(0) == name:
      if self.existPlayName(name):
        return None, 2
      else:
        return name, 0

    else:
      return None, 1


  # 昵称是否存在
  def existPlayName(self, name):
    if self.__plays is None:
      return False

    for play in self.__plays:
      if play["name"] == name:
        return True

    return False


# 几个有用的函数
class Util:
  # 格式化持续时间
  def time2str(gameTime):
    gameTime = int(gameTime)
    fmts = []
    for t in [time_today, time_hour, time_minutes, time_seconds]:
      a = gameTime // t
      gameTime %= t
      if a != 0:
        fmts.append("{:02}".format(a))

    return ":".join(fmts)


  # 排序比较器
  def cmp(first, two):
    for key in first:
      try:
        first[key] = int(first[key])
      except:
        continue

    for key in two:
      try:
        two[key] = int(two[key])
      except:
        continue

    if first["score"] != two["score"]:
      return first["score"] - two["score"]
    else:
      return two["time"] - first["time"]


  # 通用的网络请求函数
  def download(url, method="GET", params=None):
    if method == "GET":
      response = requests.get(url, params=params)
    else:
      headers = {"content-type": "application/json; charset=utf-8"}
      response = requests.post(url, json=params, headers=headers)

    if response.ok:
      return response.json()
