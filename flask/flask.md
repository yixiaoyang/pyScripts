### 工程结构

一个项目往往有很多文件，为了更好的对项目进行管理，同时也为了后期的扩展，需要好好设计一下工程的骨架结构。

```
├── app
│   ├── static
│   └── templates
├── main
│   ├── __init__.py
│   ├── errors.py
│   ├── forms.py
│   └── views.py
├── tests
│   └── __init__.py
├── README.md
├── __init__.py --初始化app包
├── config.py --应用配置信息，比如数据库配置
├── email.py
├── manage.py --脚本，比如启动服务器，与数据库交互
├── migrations
├── models.py --数据模型
├── requirements.txt
├── run.py --项目运行脚本

└── venv
```

### 安装依赖

首先，在requirenments.txt添加项目的依赖。
> Flask
> flask-mongoengine
> Flask-Script

然后使用pip安装这些依赖。

```
$ sudo pip install -r requirenments.txt
```

### 数据库
使用sqlitechemy

```
$ python run.py db init
$ python run.py db migrate
$ python run.py db upgrade

yixiaoyang@localhost /devel/git/github/pyScripts/flask/flask-read $ python run.py shell
>>> from app import db
>>> db.create_all()
>>> from app.models import Todo
>>> todo = Todo("todo content1",0)
>>> todo2 = Todo("todo content2",0)
>>> todo3 = Todo("todo content2",1)
>>> db.session.add(todo)
>>> db.session.add(todo2)
>>> db.session.add(todo3)
>>> db.session.commit()
>>> exit()

```
### 插件

- celery:在线程或机器间分发任务的机制
- dev-python/virtualenv:Virtual Python Environment builder
