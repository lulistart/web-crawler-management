from flask import Flask, request, jsonify, render_template, session
from database import db, User, Task
from werkzeug.security import generate_password_hash, check_password_hash
import random
import time
import threading

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

# 修改执行任务函数
def execute_task(task_id):
    print(f"Starting task {task_id}")  # 调试日志
    with app.app_context():
        try:
            task = Task.query.get(task_id)
            if not task:
                print(f"Task {task_id} not found")  # 调试日志
                return
            
            print(f"Task {task_id} executing...")  # 调试日志
            # 模拟执行过程
            time.sleep(5)  # 固定等待5秒
            result = random.choice([0, 1])
            
            print(f"Task {task_id} completed with result {result}")  # 调试日志
            task.update_status('finished' if result == 1 else 'failed', result)
            
        except Exception as e:
            print(f"Task {task_id} failed with error: {str(e)}")  # 调试日志
            task.update_status('failed', 0)

@app.route('/task/<int:task_id>/start', methods=['POST'])
def start_task(task_id):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    task = Task.query.get(task_id)
    if not task or task.user_id != session['user_id']:
        return jsonify({'code': 1, 'msg': '任务不存在或无权限'})
    
    task.update_status('running')
    
    # 创建并启动新线程
    thread = threading.Thread(target=execute_task, args=(task_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'code': 0, 'msg': '任务已开始'})

@app.route('/task/batch/start', methods=['POST'])
def batch_start_task():
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
        # 为每个任务创建新线程
        thread = threading.Thread(target=execute_task, args=(task.id,))
        thread.daemon = True
        thread.start()
    
    return jsonify({'code': 0, 'msg': '批量开始成功'})

@app.route('/')
def home():
    if 'user_id' not in session:
        return render_template('login.html')
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 1, 'msg': '用户名已存在'})
    
    user = User(username=username, password=generate_password_hash(password))
    user.save()
    return jsonify({'code': 0, 'msg': '注册成功'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'code': 1, 'msg': '用户名或密码错误'})
    
    session['user_id'] = user.id
    return jsonify({'code': 0, 'msg': '登录成功'})

@app.route('/task', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    data = request.json
    task = Task(
        user_id=session['user_id'],
        name=data.get('name'),
        url=data.get('url'),
        status='waiting'  # 设置初始状态
    )
    task.save()
    return jsonify({'code': 0, 'msg': '任务创建成功'})

@app.route('/task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if 'user_id' not in session:
        return jsonify({'code': 1, 'msg': '请先登录'})
    
    task = Task.query.get(task_id)
    if not task or task.user_id != session['user_id']:
        return jsonify({'code': 1, 'msg': '任务不存在或无权限'})
    
    task.delete()
    return jsonify({'code': 0, 'msg': '任务删除成功'})

@app.route('/task/<int:task_id>/status', methods=['GET'])
def get_task_status(task_id):
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

@app.route('/task/batch/create', methods=['POST'])
def batch_create_task():
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

# 在应用退出时清理
@app.teardown_appcontext
def cleanup(error):
    pass

if __name__ == '__main__':
    app.run(debug=True) 