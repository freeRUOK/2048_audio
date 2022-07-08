# --*-- Encoding: UTF-8 --*--
#! fileName: tts.py
# * 2651688427@qq.com
# 实现游戏的tts引擎部分
from ctypes import *
import json
import os
import win32com.client
import wx

# ZDSRAPI语音
class ZDSREngine:
  def __init__(self):
    self.__zdsrapi = windll.LoadLibrary(os.path.join(os.getcwd(), "zdsrapi.dll"))
    self.__zdsrapi.InitTTS.argtypes = (c_int, c_wchar_p, c_bool)
    self.__zdsrapi.Speak.argtypes = (c_wchar_p, c_bool)
    if self.__zdsrapi.InitTTS(1, "游戏通道", True) != 0 or self.__zdsrapi.GetSpeakState() <= 2:
      raise OSError()


  def isScreenReader(self):
    return True


  # 朗读文本
  def speak(self, text, interrupt):
    self.__zdsrapi.Speak(text, interrupt)


  # 是否在朗读文本
  def isSpeaking(self):
    return self.__zdsrapi.GetSpeakState()


  # 停止朗读
  def stop(self):
    self.__zdsrapi.StopSpeak()


# SAPI引擎
class SAPIEngine:
  def __init__(self, voice="Microsoft Hongyu Mobile - Chinese (Simplified, PRC)", speed=100, volume=100):
    tts = win32com.client.Dispatch("SAPI.SpVoice")
    self.__sapiEngine = tts
    self.setVoice(voice)
    self.setSpeed(speed)
    self.setVolume(volume)


 # 朗读文本
  def speak(self, text, interrupt):
    if interrupt:
      self.__sapiEngine.Speak(text, 3)
    else:
      self.__sapiEngine.Speak(text)


  # 是否为读屏软件语音接口
  def isScreenReader(self):
    return False


  # 获取所有发音角色
  def getVoices(self):
    return [voice.GetDescription() for voice in self.__sapiEngine.GetVoices()]


  # 获取当前发音角色
  def getVoice(self):
    return self.__sapiEngine.Voice.GetDescription()


  # 设置当前发音角色
  def setVoice(self, voice):
    for voice in self.__sapiEngine.GetVoices():
      if voice.GetDescription() == voice:
        self.__sapiEngine.Voice = voice


  # 获取当前音量
  def getVolume(self):
    return self.__sapiEngine.Volume


  # 设置当前音量
  def setVolume(self, value):
    if value >= 0 and value <= 100:
      self.__sapiEngine.Volume = value


  # 获取当前发音速度
  def getSpeed(self):
    return (self.__sapiEngine.Rate + 10) * 5


  # 设置当前发音速度
  def setSpeed(self, value):
    if value >= 0 and value <= 100:
      self.__sapiEngine.Rate = value // 5 - 10


# NVDA_controller语音
class NVDAControllerEngine:
  def __init__(self):
    self.__nvdaController = windll.LoadLibrary(os.path.join(os.getcwd(), "nvdaControllerClient32.dll"))
    self.__nvdaController.nvdaController_speakText.argtypes = (c_wchar_p, )
    if self.__nvdaController.nvdaController_testIfRunning() != 0:
      raise OSError()


  # 朗读文本
  def speak(self, text, interrupt):
    if interrupt:
      self.__nvdaController.nvdaController_cancelSpeech()

    self.__nvdaController.nvdaController_speakText(text)


  # 停止朗读
  def stop(self):
    self.__nvdaController.nvdaController_cancelSpeech()


  # 是否为读屏语音接口
  def isScreenReader(self):
    return True


# AISound引擎
class AISoundEngine:
  def __init__(self, voice="小燕", speed=100, volume=100):
    self.__voice = None
    self.__speed = None
    self.__volume = None
    self.__aiSound = cdll.LoadLibrary(os.path.join(os.getcwd(), "aisound.dll"))
    self.__aiSound.aisound_initialize()
    self.__aiSound.aisound_speak.argtypes = (c_char_p, c_void_p)
    self.__aiSound.aisound_configure.argtypes = (c_char_p, c_char_p)
    self.__voices = {"YanPing": "小燕", 
      "XiaoFeng": "小风", 
      "XiaoPing": "小平", 
      "BaByXu": "徐宝宝", 
      "DonaldDuck": "唐老鸭", 
      "DuoXu": "徐多", 
      "JiuXu": "徐炯", 
      "XiaoMei": "小梅（粤语）", 
      "DaLong": "大龙（粤语）"
      }
    self.setVoice(voice)
    self.setSpeed(speed)
    self.setVolume(volume)


  # 朗读文本
  def speak(self, text, interrupt):
    if interrupt:
      self.__aiSound.aisound_cancel()

    self.__aiSound.aisound_speak(text.encode(), c_void_p(0))


  # 停止朗读
  def stop(self):
    self.__aisoundEngine.aisound_cancel()


  # 是否为读屏软件语音接口
  def isScreenReader(self):
    return False


  # 获取所有发音角色
  def getVoices(self):
    results = []
    for name in self.__voices:
      results.append(self.__voices[name])

    return results


  # 获取当前发音角色
  def getVoice(self):
    return self.__voice


  # 设置当前发音角色
  def setVoice(self, name):
    for voice in self.__voices:
      if self.__voices[voice] == name:
        self.__voice = name
        self.__aiSound.aisound_configure("voice".encode(), voice.encode())


  # 获取当前音量
  def getVolume(self):
    return self.__volume


  # 设置当前音量
  def setVolume(self, value):
    if value >= 0 and value <= 100:
      self.__volume = value
      self.__aiSound.aisound_configure("volume".encode(), "{}".format(int(value * 655.35 - 32768)).encode())


  # 获取当前发音速度
  def getSpeed(self):
    return self.__speed


  # 设置当前发音速度
  def setSpeed(self, value):
    if value >= 0 and value <= 100:
      self.__speed = value
      self.__aiSound.aisound_configure("speed".encode(), "{}".format(int(value * 655.35 - 32768)).encode())


TTS_PATH = os.path.join(os.getcwd(), "setting.json")

# 集中管理所有的tts语音引擎
class Engines:
  def __init__(self):
    self.__engines = {"MS SAPI": {"name": "SAPIEngine"}, 
      "AISound": {"name": "AISoundEngine"}, 
      "争渡": {"name": "ZDSREngine"}, 
      "NVDA": {"name": "NVDAEngine"}, 
      }

    self.__ttsConfig = self.load()
    if self.isConfigure():
      self.__currentEngine = self.__newEngine(self.__ttsConfig["currentEngine"])
    else:
      self.__currentEngine = self.__newEngine("SAPIEngine")
      self.__ttsConfig["currentEngine"] = "SAPIEngine"


  # 加载tts配置信息
  def load(self):
    fp = open(TTS_PATH)
    ttsConfig = json.load(fp)["tts_config"]
    fp.close()
    return ttsConfig


  # 保存tts配置信息
  def save(self):
    fp = open(TTS_PATH, "r")
    allObj = json.load(fp)
    fp.close()
    fp = open(TTS_PATH, "w")
    allObj["tts_config"] = self.__ttsConfig
    json.dump(allObj, fp)
    fp.close()


  # 是否配置过
  def isConfigure(self):
    return len(self.__ttsConfig["engines"]) != 0


  # 打开配置tts对话框
  def configure(self):
    ttsDialog = TTSEngineDialog(self)
    ttsDialog.ShowModal()
    ttsDialog.app.Destroy()


  # 返回当前tts引擎
  def getCurrentEngine(self):
    return self.__currentEngine


  # 返回当前tts引擎的名称
  def getCurrentEngineName(self):
    return self.__ttsConfig["currentEngine"]


  # 获取当前发音角色
  def getCurrentVoice(self):
    return self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["voice"]

  # 获取当前语速
  def getCurrentSpeed(self):
    return self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["speed"]


  # 获取当前音量
  def getCurrentVolume(self):
    return self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["volume"]


  # 设置当前角色
  def setCurrentVoice(self, voice):
    if not self.__currentEngine.isScreenReader():
      if not self.__ttsConfig["currentEngine"] in self.__ttsConfig["engines"]:
        self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]] = {}

      self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["voice"] = voice
      self.__currentEngine.setVoice(voice)


  # 设置当前语速
  def setCurrentSpeed(self, speed):
    if not self.__currentEngine.isScreenReader():
      if not self.__ttsConfig["currentEngine"] in self.__ttsConfig["engines"]:
        self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]] = {}

      self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["speed"] = speed
      self.__currentEngine.setSpeed(speed)


  # 设置当前音量
  def setCurrentVolume(self, volume):
    if not self.__currentEngine.isScreenReader():
      if not self.__ttsConfig["currentEngine"] in self.__ttsConfig["engines"]:
        self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]] = {}

      self.__ttsConfig["engines"][self.__ttsConfig["currentEngine"]]["volume"] = volume
      self.__currentEngine.setVolume(volume)


  # 创建tts引擎实力
  def __newEngine(self, name):
    config = self.__ttsConfig["engines"].get(name)
    engine = None
    try:
      if name == "ZDSREngine":
        engine = ZDSREngine()
      elif name == "NVDAEngine":
        engine = NVDAControllerEngine()
      elif name == "SAPIEngine":
        if config is None:
          engine = SAPIEngine()
        else:
          engine = SAPIEngine(voice=config["voice"], speed=config["speed"], volume=config["volume"])

      elif name == "AISoundEngine":
        if config is None:
          engine = AISoundEngine()
        else:
          engine = AISoundEngine(voice=config["voice"], speed=config["speed"], volume=config["volume"])

      else:
        pass
    except OSError:
      pass

    if (not engine is None) and (not engine.isScreenReader()):
      config = {}
      config["voice"] = engine.getVoice()
      config["speed"] = engine.getSpeed()
      config["volume"] = engine.getVolume()
      self.__ttsConfig["engines"][name] = config

    return engine


  # 返回所有可选tts引擎描述和名称
  def getAllEngineInfo(self):
    return [info for info in self.__engines]


  # 根据描述返回名称
  def getByName(self, info):
    return self.__engines[info]["name"]


  # 根据名称返回描述
  def getByInfo(self, name):
    for info in self.__engines:
      if self.__engines[info]["name"] == name:
        return info


  # 选择一个tts引擎
  def selectEngine(self, name):
    if self.getByInfo(name) in self.__engines:
      engine = self.__newEngine(name)
      if engine:
        self.__currentEngine = engine
        self.__ttsConfig["currentEngine"] = name


# 配置tts引擎对话框
class TTSEngineDialog(wx.Dialog):
  def __init__(self, engines):
    self.app = wx.App()
    wx.Dialog.__init__(self, None, title="设置语音")
    self.__engines = Engines()
    self.engineLabel = wx.StaticText(self, label="语音引擎： ")
    self.engineComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
    self.engineComboBox.Bind(wx.EVT_COMBOBOX, self.OnEngineComboBoxChange)
    self.engineComboBox.Bind(wx.EVT_SET_FOCUS, self.OnComboBoxFocus)
    self.engineComboBox.Set(self.__engines.getAllEngineInfo())
    self.engineComboBox.SetStringSelection(self.__engines.getByInfo(self.__engines.getCurrentEngineName()))

    self.voiceLabel = wx.StaticText(self, label="发音角色： ")
    self.voiceComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
    self.voiceComboBox.Bind(wx.EVT_COMBOBOX, self.OnVoiceComboBoxChange)
    self.voiceComboBox.Bind(wx.EVT_SET_FOCUS, self.OnComboBoxFocus)

    self.speedLabel = wx.StaticText(self, label="发音语速： ")
    self.speedSlider = wx.Slider(self)

    self.speedSlider.Bind(wx.EVT_SLIDER, self.OnSpeedSliderChange)

    self.volumeLabel = wx.StaticText(self, label="音量： ")
    self.volumeSlider = wx.Slider(self)
    self.volumeSlider.Bind(wx.EVT_SLIDER, self.OnVolumeSliderChange)

    self.testButton = wx.Button(self, label="试听(&T)")
    self.testButton.Bind(wx.EVT_BUTTON, self.OnTestButtonClick)

    self.okButton = wx.Button(self, label="确定(&O)")
    self.okButton.Bind(wx.EVT_BUTTON, self.OnOkButtonClick)
    self.cancelButton = wx.Button(self, id=wx.ID_CANCEL, label="取消(&C)")
    self.loadTTSConfig()


  # 载入语音配置
  def loadTTSConfig(self):
    if not self.__engines.getCurrentEngine().isScreenReader():
      self.voiceComboBox.Set(self.__engines.getCurrentEngine().getVoices())
      voice = self.__engines.getCurrentEngine().getVoice()
      self.voiceComboBox.SetStringSelection(voice)
      self.speedSlider.SetValue(self.__engines.getCurrentSpeed())
      self.volumeSlider.SetValue(self.__engines.getCurrentVolume())


  # tts引擎选择发生改变
  def OnEngineComboBoxChange(self, event):
    if self.engineComboBox.Selection == -1:
      return

    engineName = self.__engines.getByName(self.engineComboBox.GetStringSelection())
    if engineName == self.__engines.getCurrentEngineName():
      return

    self.__engines.selectEngine(engineName)
    self.__SetShow(not self.__engines.getCurrentEngine().isScreenReader())
    self.loadTTSConfig()


  # 显示或隐藏tts引擎参数调节控件
  def __SetShow(self, isShow):
    self.voiceLabel.Show(isShow)
    self.voiceComboBox.Show(isShow)
    self.speedLabel.Show(isShow)
    self.speedSlider.Show(isShow)
    self.volumeSlider.Show(isShow)


  # 设置当前发音角色
  def OnVoiceComboBoxChange(self, event):
    if self.voiceComboBox.Selection != -1:
      self.__engines.setCurrentVoice(self.voiceComboBox.GetStringSelection())


  # 组合框获取焦点
  def OnComboBoxFocus(self, event):
    obj = event.GetEventObject()
    if obj.Selection == -1 and obj.GetSize() != 0:
      obj.Selection = 0


  # 设置当前语速
  def OnSpeedSliderChange(self, event):
    self.__engines.setCurrentSpeed(self.speedSlider.GetValue())


  # 设置当前音量
  def OnVolumeSliderChange(self, event):
    self.__engines.setCurrentVolume(self.volumeSlider.GetValue())


  # 测试当前tts引擎
  def OnTestButtonClick(self, event):
    self.__engines.getCurrentEngine().speak("君不见黄河之水天上来，奔流到海不复回， 君不见高堂明镜悲白发， 朝如青丝暮成雪", True)


  # 保存当前tts参数并关闭对话框
  def OnOkButtonClick(self, event):
    self.__engines.save()
    self.EndModal(wx.ID_OK)
