from flask import Flask, request, jsonify, render_template, session
from database import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash
import random
import time
import threading

# Flask应用配置部分
def create_app():
    """
    创建并配置Flask应用
    - 设置密钥
    - 配置数据库
    - 初始化数据库
    """
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'  # 用于session加密
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'  # 数据库URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭FSAQLAlchemy的事件系统
    
    # 初始化数据库
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

# 任务执行相关函数
def execute_task(task_id):
    """
    异步执行任务的函数
    Args:
        task_id: 任务ID
    """
    print(f"Starting task {task_id}")
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            if not task:
                print(f"Task {task_id} not found")
                return
            
            print(f"Task {task_id} executing...")
            # 模拟任务执行
            time.sleep(5)
            result = random.choice([0, 1])
            
            print(f"Task {task_id} completed with result {result}")
            task.update_status('finished' if result == 1 else 'failed', result)
            
        except Exception as e:
            print(f"Task {task_id} failed with error: {str(e)}")
            task.update_status('failed', 0)

# 路由处理部分
@app.route('/')
def home():
    """首页路由：未登录时显示登录页面，登录后显示任务管理页面"""
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册路由
    GET: 返回注册页面
    POST: 处理注册请求
    """
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 1, 'msg': '用户名已存在'})
    
    # 创建新用户
    user = User(username=username, password=generate_password_hash(password))
    user.save()
    return jsonify({'code': 0, 'msg': '注册成功'})

@app.route('/login', methods=['POST'])
def login():
    """
    用户登录路由
    验证用户名和密码，成功后设置session
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'code': 1, 'msg': '用户名或密码错误'})
    
    session['user_id'] = user.id
    return jsonify({'code': 0, 'msg': '登录成功'})

# 任务管理相关路由
@app.route('/task', methods=['POST'])
def create_task():
    """创建单个任务"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    data = request.json
    task = Task(
        user_id=session['user_id'],
        name=data.get('name'),
        url=data.get('url'),
        status='waiting'
    )
    task.save()
    return jsonify({'code': 0, 'msg': '任务创建成功'})

@app.route('/task/batch/create', methods=['POST'])
def batch_create_task():
    """批量创建任务"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    data = request.json
    tasks_data = data.get('tasks', [])
    
    if not tasks_data:
        return jsonify({'code': 1, 'msg': '任务数据不能为空'})
    
    try:
        for task_data in tasks_data:
            task = Task(
                user_id=session['user_id'],
                name=task_data.get('name'),
                url=task_data.get('url'),
                status='waiting'
            )
            task.save()
        return jsonify({'code': 0, 'msg': f'成功创建 {len(tasks_data)} 个任务'})
    except Exception as e:
        return jsonify({'code': 1, 'msg': f'创建任务失败：{str(e)}'})

@app.route('/task/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    """启动单个任务"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    task = Task.query.get(task_id)
    if not task or task.user_id != session['user_id']:
        return jsonify({'code': 1, 'msg': '任务不存在或无权限'})
    
    task.update_status('running')
    
    # 创建新线程执行任务
    thread = threading.Thread(target=execute_task, args=(task_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'code': 0, 'msg': '任务已开始'})

@app.route('/task/batch/start', methods=['POST'])
def batch_start_task():
    """批量启动任务"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    data = request.json
    task_ids = data.get('task_ids', [])
    
    tasks = Task.query.filter(
        Task.id.in_(task_ids),
        Task.user_id == session['user_id'],
        Task.status == 'waiting'
    ).all()
    
    for task in tasks:
        task.update_status('running')
        thread = threading.Thread(target=execute_task, args=(task.id,))
        thread.daemon = True
        thread.start()
    
    return jsonify({'code': 0, 'msg': '批量开始成功'})

@app.route('/task/<int:task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    task = Task.query.get(task_id)
    if not task or task.user_id != session['user_id']:
        return jsonify({'code': 1, 'msg': '任务不存在或无权限'})
    
    return jsonify({
        'code': 0,
        'data': {
            'status': task.status,
            'result': task.result
        }
    })

@app.route('/task/list', methods=['GET'])
def task_list():
    """获取任务列表"""
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    tasks = Task.query.filter_by(user_id=session['user_id']).all()
    task_list = [{
        'id': task.id,
        'name': task.name,
        'url': task.url,
        'status': task.status,
        'result': task.result,
        'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for task in tasks]
    
    return jsonify({
        'code': 0,
        'msg': '',
        'count': len(task_list),
        'data': task_list
    })

@app.route('/task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    task = Task.query.get(task_id)
    if not task or task.user_id != session['user_id']:
        return jsonify({'code': 1, 'msg': '任务不存在或无权限'})
    
    task.delete()
    return jsonify({'code': 0, 'msg': '任务删除成功'})

@app.route('/task/batch/delete', methods=['POST'])
def batch_delete_task():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    data = request.json
    task_ids = data.get('task_ids', [])
    
    tasks = Task.query.filter(
        Task.id.in_(task_ids),
        Task.user_id == session['user_id']
    ).all()
    
    for task in tasks:
        task.delete()
    
    return jsonify({'code': 0, 'msg': '批量删除成功'})

# 在应用退出时清理
@app.teardown_appcontext
def cleanup(error):
    pass

if __name__ == '__main__':
    app.run(debug=True) 