from flask import send_from_directory, request, render_template, g
from praat import app, create_group, User, Group, Audio, AudioAnnotation, delete_group
from flask_login import login_required
import json
from forms import GroupCreationForm


@app.route('/membership', methods=['GET'])
@login_required
def show_membership():
    return render_template('membership.html')


@app.route('/ownership', methods=['GET'])
@login_required
def show_ownership():
    return render_template('ownership.html')


@app.route('/', methods=['GET'])
@login_required
def index():
    u = g.user
    user = u.details()
    group = Group.query.get(u.current_group_id)
    context = request.args.get('context') or 'ownership'
    annotation_id = request.args.get('annotation_id', '')
    audios = list(group.audios)
    annotations = []
    if not audios:
        audio = {}
    else:
        # TODO: may support multiple audios per project(group)
        # TODO: deal with audio versions
        audio = audios[0].summary()
        for a in audios[0].annotations:
            annotations.append(a.summary())
    if context == 'workspace':
        annotation = AudioAnnotation.query.get(annotation_id)
        if annotation and annotation.audio_id == audio.get('id'):
            return render_template('workspace_base.html', context=context, user=user, audio=audio, annotations=annotations, annotation=annotation.summary())
        elif annotations:
            return render_template('workspace_base.html', context=context, user=user, audio=audio, annotations=annotations)
        elif audio:
            return render_template('workspace_base.html', context=context, user=user, audio=audio)
        else:
            # TODO: redirect to audio selection?
            return render_template('workspace_base.html', context=context, user=user)
    elif context == 'ownership':
        return show_ownership()
    else:
        return show_membership();

@app.route('/audioSelection.html', methods=['GET'])
@login_required
def fetch_audio_selection():
    return render_template("audioSelection.html")

@app.route('/main.html')
@login_required
def original_index():
    return render_template("main.html")

@app.route('/auth/groups', methods=['PUT', 'DELETE'])
@login_required
def create_new_group():
    user = User.query.filter_by(google_id=userinfo['id']).first()
    if request.method == 'PUT':
        gName = json.loads(request.headers['data'])['groupName']
        nGroup = create_group(user, gName)
    if request.method == 'DELETE':
        group_id = json.loads(request.headers['data'])['groupId']
        dGroup = delete_group(user, group_id);
    return index()

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

