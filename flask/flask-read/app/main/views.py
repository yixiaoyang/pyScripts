from datetime import datetime
from flask import render_template, session, redirect, url_for, escape, request, flash
from ..models import Todo
from . import main
from .. import db

#from ..models import User
#from .froms import NameForm

@main.route('/',methods=['get', 'post'])
def index():
	return render_template('index.html')

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


@main.route('/todo/<id>/del/',methods=['get','post'])
def todos_del(id):
	id = request.form['id']
	print('id=%d' % id)
	todo = Todo.query.filter_by(id=id).first()
	if todo is None:
		abort(404)
	db.session.delete(todo)
	db.session.commit()
	return redirect(url_for('index'))

@main.route('/todo/<id>/',methods=['get','post', 'delete'])
def todos_show(id):
	print('method = %s' % request)
	if request.method == 'GET':
		todo = Todo.query.filter_by(id=id).first()
		if todo is None:
			abort(404)
		return render_template('todo/show.html', todo=todo)
	elif request.method == 'DELETE':
		return redirect(url_for('index'))
