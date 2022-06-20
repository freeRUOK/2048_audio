# --*-- Encoding: UTF-8 --*--
#! filename: routes.py
# * 2651688427@qq.com

# 路由处理
import json
from flask import request
from apps import app
from apps.data_manager import *

top = Top()
names = ["hash", "name", "score", "time"]
# 响应首页
@app.route("/")
def index():
  return app.send_static_file("html/index.html")


# 响应全部数据请求
@app.route("/do-all")
def do_all():
  if "count" in request.args:
    reqCount = int(request.args.get("count"))
    resCount = data.count()
    if resCount <= reqCount:
      return "[]"

  return json.dumps([json.loads(i) for i in top.getAll()])


# 响应更新数据
@app.route("/do-update", methods=["POST"])
def do_update():
  obj = {}
  for name in names:
    try:
      value = request.json[name]
    except KeyError:
      return json.dumps({"error_code": ERROR_FAIL, "error_message": "不完整的数据", "data": request.json})

    obj[name] = value

  error_code = top.updatePlay(obj["hash"], json.dumps(obj))
  if error_code == ERROR_OK:
    return json.dumps({"error_code": error_code,"message": "更新完成"})
  else:
    return json.dumps({"error_code": error_code,"message": "更新失败"})


# 初始化新数据
@app.route("/do-init")
def do_init():
  hash = top.initPlay()
  if hash:
    return json.dumps({"error_code": ERROR_OK, "message": "初始化成功", "hash": hash})
  else:
    return json.dumps({"error_code": ERROR_FAIL, "message": "初始化失败"})
