from flask import send_from_directory, request, render_template
from praat import app
from flask_login import login_required

@app.route('/', methods=['GET'])
@login_required
def index():
    context = request.args.get('context') or 'workspace'
    audiofile="OldPart2.mp3"
    user={'username': 'Nana Liu'}
    return render_template('base.html', context='membership', user=user)

@app.route('/index.html')
@login_required
def original_index():
    return app.send_static_file("index.html")

@app.route('/googleb4aacaa01acbdce3.html')
def goog_verify():
    return app.send_static_file('googleb4aacaa01acbdce3.html')

@app.route('/praatapidocs')
def Praatapidocs():
    return app.send_static_file("praatapidocs.html")

@app.route('/elanapidocs')
def ELANapidocs():
    return app.send_static_file("elanapidocs.html")

@app.route('/js/<jsfile>')
def getJS(jsfile):
    return send_from_directory("static/js/", jsfile)

@app.route('/css/<cssfile>')
def getCSS(cssfile):
    return send_from_directory("static/css/", cssfile)

@app.route('/img/<imgfile>')
def getImage(imgfile):
    return send_from_directory("static/img/", imgfile)

