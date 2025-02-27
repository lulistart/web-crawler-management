# Flask Web 应用开发指南

## 1. 项目结构说明

### 1.1 核心文件
- `app.py`: 主应用文件，包含路由和业务逻辑
- `database.py`: 数据库模型定义
- `templates/`: HTML模板文件
- `static/`: 静态文件（JS、CSS等）

### 1.2 关键概念
1. **路由系统**
   - 使用装饰器 `@app.route()` 定义URL路由
   - 支持多种HTTP方法（GET、POST等）
   - 可以包含URL参数

2. **模板系统**
   - 使用Jinja2模板引擎
   - 支持模板继承和复用
   - 可以传递变量到模板

3. **数据库操作**
   - 使用SQLAlchemy ORM
   - 模型定义和数据库操作分离
   - 支持多种数据库后端

4. **用户会话**
   - 使用Flask Session管理用户状态
   - 支持加密的客户端会话
   - 可以存储用户认证信息

## 2. 核心功能实现

### 2.1 用户认证
1. **注册功能**
   - 密码加密存储
   - 用户名唯一性验证
   - 表单数据验证

2. **登录功能**
   - 密码验证
   - Session管理
   - 登录状态维护

### 2.2 任务管理
1. **任务创建**
   - 单个任务创建
   - 批量任务创建
   - 任务参数验证

2. **任务执行**
   - 异步执行
   - 状态更新
   - 结果记录

3. **任务监控**
   - 实时状态查询
   - 执行结果展示
   - 批量操作支持

## 3. 关键技术点

### 3.1 异步任务处理
```python
def execute_task(task_id):
    with app.app_context():
        # 在新线程中执行任务
        # 更新任务状态
```

### 3.2 数据库操作
```python
class Task(db.Model):
    # 定义模型
    def save(self):
        db.session.add(self)
        db.session.commit()
```

### 3.3 用户认证
```python
@app.route('/login', methods=['POST'])
def login():
    # 验证用户
    # 设置session
    # 返回结果
```

## 4. 最佳实践

1. **安全性考虑**
   - 密码加密存储
   - SQL注入防护
   - XSS防护
   - CSRF防护

2. **性能优化**
   - 数据库查询优化
   - 异步任务处理
   - 缓存使用

3. **代码组织**
   - 模块化设计
   - 职责分离
   - 代码复用

## 5. 扩展开发

1. **添加新功能**
   - 定义新的模型
   - 添加相应的路由
   - 实现业务逻辑
   - 创建前端界面

2. **自定义爬虫逻辑**
   - 修改execute_task函数
   - 添加错误处理
   - 保存爬取结果

3. **优化用户体验**
   - 添加进度显示
   - 优化错误提示
   - 改进界面交互

## 6. 调试技巧

1. **使用debug模式**
   ```python
   app.run(debug=True)
   ```

2. **日志记录**
   ```python
   app.logger.debug('调试信息')
   app.logger.error('错误信息')
   ```

3. **数据库调试**
   ```python
   # 打印SQL语句
   app.config['SQLALCHEMY_ECHO'] = True
   ``` 