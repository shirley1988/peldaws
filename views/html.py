from flask import send_from_directory
from praat import app

@app.route('/')
def index():
   return app.send_static_file("index.html")

@app.route('/apidocs')
def apidocs():
   return app.send_static_file("apidocs.html")

@app.route('/js/<jsfile>')
def getJS(jsfile):
   return send_from_directory("static/js/", jsfile)

@app.route('/css/<cssfile>')
def getCSS(cssfile):
   return send_from_directory("static/css/", cssfile)

@app.route('/img/<imgfile>')
def getImage(imgfile):
   return send_from_directory("static/img/", imgfile)

