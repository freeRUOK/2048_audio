## 服务器端开发说明

  服务器端数据用redis来存储

### 项目依赖

### python3

* flask  web框架
* redis python的redis接口

#### js

* vue3 浏览器前端UI

*axios 浏览器前端http请求支持

### 文件说明

* apps/__init__.py 初始化flask项目
* apps/data_manager.py 数据管理模块

* routes.py web路由管理模块

* static/html/index.html web前端主页

* static/js/vueapp.js vue3前台UI实现 注意该文件已经嵌入到web前端主页html文件里了

* app.py flask项目入口

* run.sh 启动项目的脚本
