import os 

from app import create_app, db
from app.models import User,Todo

from flask import url_for
from flask.ext.script import Manager,Shell
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.scss import Scss

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# initialization for componet
manager = Manager(app)
migreate = Migrate(app,db)
Scss(app)

def make_shell_context():
	return dict(app=app, db=db)

manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

# python run.py list_routes
@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:32s} {:32s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    
    for line in sorted(output):
        print line

if __name__ == '__main__':
	manager.run()