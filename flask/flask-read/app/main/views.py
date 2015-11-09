from datetime import datetime
from flask import render_template, session, redirect, url_for
from ..models import Todo
from . import main

#from ..models import User
#from .froms import NameForm
#from .. import db

@main.route('/',methods=['get', 'post'])
def index():
	return render_template('index.html')

@main.route('/todo/',methods=['get', 'post'])
def todos():
	todos = Todo.query.all()
	todos_count = Todo.query.count()
	return render_template('todo/index.html', todos=todos,todos_count=todos_count)