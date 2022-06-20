# --*-- Encoding: UTF-8 --*--
#! fileName: tts.py
# * 2651688427@qq.com
# 实现游戏的tts引擎部分
from ctypes import *
import os
import win32com.client

# ZDSRAPI语音
class ZDSREngine:
  def __init__(self):
    self.__zdsrapi = windll.LoadLibrary(os.path.join(os.getcwd(), "zdsrapi.dll"))
    self.__zdsrapi.InitTTS.argtypes = (c_int, c_wchar_p, c_bool)
    self.__zdsrapi.Speak.argtypes = (c_wchar_p, c_bool)
    if self.__zdsrapi.InitTTS(1, "游戏通道", True) != 0 or self.__zdsrapi.GetSpeakState() <= 2:
      raise OSError()


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
  def __init__(self):
    tts = win32com.client.Dispatch("SAPI.SpVoice")
    tts.Volume = 100
    tts.Rate = 300
    for voice in tts.GetVoices():
      if voice.GetDescription() == "Microsoft Hongyu Mobile - Chinese (Simplified, PRC)":
        tts.Voice = voice

    self.__tts = tts


 # 朗读文本
  def speak(self, text, interrupt):
    if interrupt:
      self.__tts.Speak(text, 3)
    else:
      self.__tts.Speak(text)


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
