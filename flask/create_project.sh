#!/bin/bash
ROOT=$1

echo $ROOT

mkdir $ROOT/app/templates/ -p
mkdir $ROOT/app/templates/static/ -p
touch $ROOT/app/templates/static/404.html
touch $ROOT/app/templates/static/500.html
touch $ROOT/app/__init__.py
touch $ROOT/app/models.py

mkdir $ROOT/app/main
touch $ROOT/app/main/__init__.py
touch $ROOT/app/main/errors.py
touch $ROOT/app/main/forms.py
touch $ROOT/app/main/views.py

mkdir $ROOT/migrations
mkdir $ROOT/tests
touch $ROOT/tests/__init__.py
mkdir $ROOT/venv

touch $ROOT/__init__.py
touch $ROOT/requirements.txt
touch $ROOT/config.py
touch $ROOT/run.py
touch $ROOT/README.md


