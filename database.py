from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db():
    from app import app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crawler.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, running, finished, failed
    result = db.Column(db.Integer, nullable=True)  # 执行结果：1成功，0失败
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update_status(self, status, result=None):
        self.status = status
        if result is not None:
            self.result = result
        db.session.commit() 