# Web Crawler Task Management System

一个基于 Flask 和 Layui 的简单爬虫任务管理系统，支持多用户、批量任务管理和实时状态监控。

## 功能特点

- 用户系统
  - 用户注册
  - 用户登录
  - 会话管理

- 任务管理
  - 单个任务创建
  - 批量任务创建（支持文本导入）
  - 任务状态实时监控
  - 批量任务操作（开始/删除）
  - 异步任务执行

## 技术栈

- 后端
  - Python Flask
  - SQLAlchemy
  - SQLite
  - Python Threading

- 前端
  - Layui
  - jQuery
  - Fetch API

## 项目结构
project/
├── app.py # Flask应用主文件
├── database.py # 数据库模型定义
├── static/
│ └── js/
│ └── main.js # 前端JavaScript逻辑
└── templates/
├── index.html # 主页面模板
├── login.html # 登录页面模板
└── register.html # 注册页面模板


## 快速开始

1. 安装依赖
bash
pip install -r requirements.txt

2. 启动应用
bash

python app.py
3. 访问应用

http://localhost:5000

## 项目结构
project/
├── app.py # Flask应用主文件
├── database.py # 数据库模型定义
├── static/
│ └── js/
│ └── main.js # 前端JavaScript逻辑
└── templates/
├── index.html # 主页面模板
├── login.html # 登录页面模板
└── register.html # 注册页面模板


## 使用说明

### 1. 用户管理
- 访问首页时自动跳转到登录页面
- 新用户需要先完成注册
- 登录后可以进行任务管理

### 2. 任务管理
- 单个任务创建
  - 点击"新建任务"按钮
  - 输入任务名称和URL
  - 点击提交

- 批量任务创建
  - 点击"批量新建"按钮
  - 按照格式输入任务列表：
    ```
    任务名称1-http://example1.com
    任务名称2-http://example2.com
    ```
  - 点击提交

- 任务操作
  - 单个任务开始：点击对应任务的"开始"按钮
  - 批量开始：选择多个任务后点击"批量开始"
  - 删除任务：点击"删除"或"批量删除"按钮

### 3. 任务状态
- 等待执行（灰色）：初始状态
- 执行中（蓝色）：任务正在执行
- 执行成功（绿色）：任务完成
- 执行失败（红色）：任务失败

## 开发说明

### 添加自定义爬虫逻辑

在 `app.py` 中修改 `execute_task` 函数：

```python
def execute_task(task_id):
    with app.app_context():
        task = Task.query.get(task_id)
        try:

            # 添加自定义爬虫逻辑
            result = your_crawler_function(task.url)
            task.update_status('finished' if result else 'failed', result)
            except Exception as e:
            task.update_status('failed', 0)
```python


## 注意事项

1. 本项目为演示用途，生产环境使用需要：
   - 修改 secret_key
   - 使用生产级数据库
   - 添加必要的安全措施
   - 使用生产级 WSGI 服务器

2. 任务执行采用线程池，注意控制并发数量


## License

[MIT License](LICENSE)


