from datetime import datetime
from flask import render_template, session, redirect, url_for, escape, request, flash, abort 
from ..models import Todo
from . import main
from .. import db

from flask.ext.login import login_required,login_user

#from ..models import User
#from .froms import NameForm

@main.route('/',methods=['get', 'post'])
def index():
	return render_template('index.html')

#####################################################################
# Todo
#####################################################################
@main.route('/todo/',methods=['get', 'post'])
def todos():
	error = None
	if request.method == 'POST':
		content = request.form['content']
		if not content:
			error = "Invalid Content"
		else:
			todo = Todo(content=content,status=0)
			db.session.add(todo)
			db.session.commit()
			print todo
			flash('You were successfully inssert new todo',"success")
	todos = Todo.query.all()
	todos_count = Todo.query.count()
	return render_template('todo/index.html', todos=todos,todos_count=todos_count)

# test:curl -i http://localhost:5000/todo/1/ -X DELETE
@main.route('/todo/<id>/',methods=['get','post', 'delete'])
def todos_show(id):
	print('method = %s' % request)
	if request.method == 'GET':
		todo = Todo.query.filter_by(id=id).first()
		if todo is None:
			abort(404)
		return render_template('todo/show.html', todo=todo)
	elif request.method == 'DELETE':
		# url_for in blueprint 'url_for(BlueprintName.FuncName)' 
		return redirect(url_for('main.todos'))

@main.route('/todo/del/<id>',methods=['get','post','delete'])
def todos_del(id):
	#id = request.form['id']
	print('id=%s' % id)
	todo = Todo.query.filter_by(id=id).first()
	if todo is None:
		abort(404)
	db.session.delete(todo)
	db.session.commit()
	return redirect(url_for('main.todos'))


#####################################################################
# User
#####################################################################
@main.route('/user/login/', methods=['get'])
@main.route('/user/login/', methods=['post'])
def login():
	print('method = %s' % request)
	return render_template('user/login.html')

	
