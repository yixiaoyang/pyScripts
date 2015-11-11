import datetime
from app import db
from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager

class User(UserMixin,db.Model):
	__tablename = 'users'
	id = db.Column(db.Integer,primary_key=True)
	email = db.Column(db.String(64),unique=True, index=True)
	username = db.Column(db.String(64),unique=True, index=True)
	password_hash = db.Column(db.String(128))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	@property
	def password(self):
		raise AttributeError('Password is not readable attriute')
	
	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self,password):
		return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))

class Todo(db.Model):
	content = db.Column(db.String(64))
	time = db.Column(db.DateTime, default=datetime.datetime.now())
	status = db.Column(db.Integer,default=0)
	id = db.Column(db.Integer, primary_key=True)

	def __init__(self, content, status):
		self.content = content
		self.status = status

	def _repr_(self):
		return '<Todo %r>' % self.id

