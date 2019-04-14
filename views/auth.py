from flask import send_from_directory
from flask import g, jsonify, request
from praat import app
import praat
import utils
import json
from flask_login import login_required
from storage import get_storage_service
import datetime


# retrieve a list of users
@app.route('/api/auth/users', methods=['GET'])
def api_list_users():
    details = request.args.get('details')
    all_users = praat.User.query.all()
    if utils.is_true(details):
        res = list(u.details() for u in all_users)
    else:
        res = list(u.summary() for u in all_users)
    return jsonify(res)


# retrieve a list of groups
@app.route('/api/auth/groups', methods=['GET'])
def api_list_groups():
    details = request.args.get('details')
    all_groups = praat.Group.query.all()
    if utils.is_true(details):
        res = list(gp.details() for gp in all_groups)
    else:
        res = list(gp.summary() for gp in all_groups)
    return jsonify(res)


# current user's profile
@app.route('/auth/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = g.user
    if request.method == 'GET':
        return jsonify(user.details())
    # current only allow to update current group
    _group = None
    print request.headers
    _gId = request.json.get('groupId')
    _gName = request.json.get('groupName')
    if _gId:
        _group = praat.Group.query.get(_gId)
    if _group is None and _gName:
        _group = praat.Group.query.filter_by(name=_gName).first()
    if _group is None:
        return "Invalid target group info"
    if user in _group.members:
        print "old group id: " + user.current_group_id
        print "new group id: " + _group.id
        user.current_group_id = _group.id
        praat.db_session.commit()
        return "Successfully updated user's current group"
    return "User is not a member of target group"


# retrieve groups owned by current user
# or create a new group
@app.route('/auth/groups', methods=['GET', 'POST'])
@login_required
def groups():
    print 'get or post a group'
    operator = g.user
    if operator is None:
        operator = praat.User.query.first()
    if request.method == 'GET':
        res = {
            'ownership': group_summary(operator.ownership),
            'membership': group_summary(operator.membership),
        }
        print 'returning a group'
        return jsonify(res)
    else:
        _name = request.json.get('groupName')
        if not _name:
            return "Invalid group name"
        _g = praat.Group.query.filter_by(name=_name).first()
        if _g is not None:
            return "Group of name %s already exists" % (_name)
        praat.create_group(operator, _name)
        return "User %s created group %s" % (operator.name, _name)


def group_summary(groups):
    return list(gp.summary() for gp in groups)


def find_user(uid=None, email=None):
    if uid is None and email is None:
        return None
    if uid is not None:
        return praat.User.query.get(uid)
    return praat.User.query.filter_by(email=email).first()



# retrieve or update group info
@app.route('/auth/groups/<gid>', methods=['GET', 'POST'])
@login_required
def group_ops(gid):
    operator = g.user
    group = praat.Group.query.get(gid)
    if group is None:
        return "Group %s does not exist" % (gid)
    if operator is None:
        operator = praat.User.query.first()
    if request.method == 'GET':
        return jsonify(group.details())

    allowed_actions = ['add', 'remove', 'transfer']
    if not praat.is_owner(operator, group):
        return "User %s has no permission to update group %s" % (operator.name, group.name)
    action = request.json.get('action', '').lower()
    if not action in allowed_actions:
        return "Invalid action %s" % (action)
    user = find_user(uid=request.json.get('userId'), email=request.json.get('userEmail'))
    if user is None:
        return "User not found"
    print "Operator name: %s , id: %s" % (operator.name, operator.id)
    print "User name: %s , id: %s" % (user.name, user.id)
    print "Group name: %s , id: %s" % (group.name, group.id)
    if action == 'add':
        praat.add_user_to_group(operator, user, group)
    elif action == 'remove':
        praat.remove_user_from_group(operator, user, group)
    else:
        praat.transfer_group(operator, user, group)
    return "User %s updates group %s - action: %s, target: %s" % (
            operator.name, group.name, action, user.name)


@app.route('/auth/audios/<audio>/annotations', methods=['GET', 'POST'])
@login_required
def annotation_ops(audio):
    user = g.user
    group = praat.Group.query.get(user.current_group_id)
    storage_svc = get_storage_service(praat.app.config)
    if request.method == 'GET':
        # TODO: handle real requests
        resp = {"status": "success"}
        return jsonify(resp)
    payload = request.json
    # TODO: handle real request
    resp = {"status": "success", "payload": payload}
    return jsonify(resp)


@app.route('/auth/groups/<gid>/audios', methods=['GET', 'POST'])
@login_required
def group_audio_ops(gid):
    user = g.user
    group = praat.Group.query.get(gid)
    params = request.json or request.args
    return generic_audio_ops(user, group, request.method, request.files.get('audio'), params)

@app.route('/auth/audios', methods=['GET', 'POST'])
@login_required
def audio_ops():
    user = g.user
    group = praat.Group.query.get(user.current_group_id)
    params = request.json or request.args
    return generic_audio_ops(user, group, request.method, request.files.get('audio'), params)

@app.route('/auth/audios/<audio>', methods=['GET', 'POST'])
@login_required
def single_audio_ops(audio):
    audio = praat.Audio.query.get(audio)
    if audio is None:
        return "Audio file not found"
    storage_svc = get_storage_service(praat.app.config)
    info = audio.summary()
    info['versions'] = storage_svc.show_versions(audio.location)
    return jsonify(info)


def generic_audio_ops(user, group, method, audio=None, params=None):
    if group is None:
        return "Group does not exist"
    storage_svc = get_storage_service(praat.app.config)
    if method == 'GET':
        #g_info = group.details()
        #return jsonify(g_info['details']['audios'])
        resp = []
        for audio in group.audios:
            info = audio.summary()
            if utils.is_true(params.get('show_versions')):
                info['versions'] = storage_svc.show_versions(audio.location)
            resp.append(info)
        print resp
        return jsonify(resp)

    if not audio or not audio.filename:
        # If no audio file, stop
        status = "No audio file"
        audioName = ""
    elif not utils.isSound(audio.filename):
        # Stop if uploaded file is not a audio
        status = "Unknown file type"
        audioName = audio.filename
    else:
        audioName = audio.filename
        data = audio.read()
        key = utils.generate_id(group.id + audioName)
        attrs = {
            'created_by': user.email,
        }
        audioObj = praat.Audio.query.filter_by(location=key).first()
        storage_svc.put(key, data, attrs)
        if audioObj is None:
            print 'Creating new audio file'
            audioObj = praat.Audio(audioName, user, group, key)
            praat.db_session.add(audioObj)
            praat.db_session.commit()
        else:
            print audioObj.summary()
            audioObj.updated_at = datetime.datetime.utcnow()
            praat.db_session.commit()
            print 'Updating existing audio file'
        status = "Success"

    result = {
        "status": status,
        "audio": audioName
    }
    return jsonify(result)

