from app import db
from flask.ext.sqlalchemy import SQLAlchemy
import datetime

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