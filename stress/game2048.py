# --*-- Encoding: UTF-8 --*--
#! filename: 2048.py
# * 2651688427@qq.com

import os
import random
import msvcrt

DIRECTION_UP = 80
DIRECTION_DOWN = 72
DIRECTION_LEFT = 77
DIRECTION_RIGHT = 75
CTRL_UP = DIRECTION_DOWN
CTRL_DOWN = DIRECTION_UP
CTRL_LEFT = DIRECTION_RIGHT
CTRL_RIGHT = DIRECTION_LEFT
CTRL_QUIT = ord("q")

class Game:
  def __init__(self):
    self.map = [0 for i in range(16)]
    self.rowLen = 4
    self.numCount = 0
    self.gameOver = False


  def get_row_pointers(self, direction, rowNum):
    allLen = len(self.map)
    rowLen = self.rowLen
    if direction == DIRECTION_LEFT or direction == DIRECTION_RIGHT:
      begin = rowLen * rowNum
      end = begin + rowLen
      step = 1
    else:
      begin = rowNum
      end = allLen
      step = rowLen

    pointers = [i for i in range(begin, end, step)]
    if direction == DIRECTION_DOWN or direction == DIRECTION_RIGHT:
      pointers.reverse()

    return pointers


  def merge(self, left, right):
    map = self.map
    if map[left] == 0 and map[right] == 0:
      return 2
    elif map[left] == 0 and map[right] != 0 or map[left] != 0 and map[right] != 0 and map[left] != map[right]:
      return 1
    elif  map[left] != 0 and map[right] == 0:
      map[left], map[right] = map[right], map[left]
      return 0
    else:
      map[right] += map[left]
      map[left] = 0
      self.numCount -= 1
      return 0


  def move(self, direction):
    map = self.map
    for rowNum in range(self.rowLen):
      ps = self.get_row_pointers(direction, rowNum)
      pos = 0
      while pos + 1 < len(ps):
        pos += self.merge(ps[pos], ps[pos + 1])


  def print(self):
    os.system("cls")
    map = self.map
    allLen = len(self.map)
    rowLen = self.rowLen
    for i in range(allLen):
      if (i + 1) % rowLen != 0:
        print(end="{} - ".format(map[i]))
      else:
        print(end="{}\n".format(map[i]))


  def make_random_number(self):
    if self.numCount >= len(self.map):
      return

    while True:
      rIndex = random.randint(0, len(self.map) - 1)
      if self.map[rIndex] == 0:
        self.map[rIndex] = (2 if random.randint(0, 9) < 8 else 4)
        self.numCount += 1
        break


  def setGameOver(self):
    if self.numCount < len(self.map):
      return

    map = self.map
    for rowNum in range(self.rowLen):
      leftPs, upPs = self.get_row_pointers(DIRECTION_LEFT, rowNum), self.get_row_pointers(DIRECTION_UP, rowNum)
      for i in range(1, self.rowLen):
        if map[leftPs[i - 1]] == map[leftPs[i]] or map[upPs[i - 1]] == map[upPs[i]]:
          return

    self.gameOver = True


  def run(self):
    self.make_random_number()
    self.make_random_number()
    self.print()
    while not self.gameOver:
      keycode = ord(msvcrt.getch())
      if keycode == 224:
        keycode = ord(msvcrt.getch())

      if keycode == CTRL_UP or keycode == CTRL_DOWN or keycode == CTRL_LEFT or keycode == CTRL_RIGHT:
        self.move(keycode)
        self.make_random_number()
        self.make_random_number()
        self.setGameOver()
        self.print()
      elif keycode == CTRL_QUIT:
        break

    if self.gameOver:
      print("--------------\n很遗憾…… 游戏失败了！ 最大合并数字为： {}".format(max(self.map)))
    else:
      print("----------------\n合并到的最大数字是： {}".format(max(self.map)))

if __name__ == "__main__":
  game = Game()
  game.run()
