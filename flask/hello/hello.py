from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
   return "<h5>hello world</h5>"

@app.route('/user/<name>')
def user(name):
   return "<h5>hello %s</h5>" % name

if __name__ == '__main__':
   app.run(debug=True)
