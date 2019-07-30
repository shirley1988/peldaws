from flask import send_from_directory
from flask import g, jsonify, request
from flask import redirect
from flask import render_template
from praat import app
from forms import GroupCreationForm
import praat
import utils
import json
from flask_login import login_required
from storage import get_storage_service
import datetime
import base64
import difflib

@app.route('/newgroup', methods=['GET'])
@login_required
def show_group_creation(error=None):
    form = GroupCreationForm()
    return render_template('newgroup.html', form=form, error=error)


# retrieve a list of users
@app.route('/api/auth/users', methods=['GET'])
@login_required
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


@app.route("/groups", methods=['GET', 'POST'])
@login_required
def create_group_via_form():
    operator = g.user
    form = GroupCreationForm()
    if request.method == 'GET':
        return render_template('newgroup.html', form=form)
    _name = form.groupName.data.strip()
    print "User %s is creating group %s" % (operator.email, _name)
    res = create_new_group(operator, _name)
    if res['result'] == 'success':
        return redirect('/ownership')
    return render_template('newgroup.html', form=form, error=res['message'])

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
            return jsonify({
                "result": "fail",
                "message": "Missing group name."
            })
        return jsonify(create_new_group(operator, _name))

def create_new_group(operator, _name):
    if len(_name) < 4 or len(_name) > 200:
        return {
            "result": "fail",
            "message": "Group name must be between 4 to 200 characters"
        }
    _g = praat.Group.query.filter_by(name=_name).first()
    if _g is not None:
        return {
            "result": "fail",
            "message": "Group " + _name + " already exists."
        }
    try:
        praat.create_group(operator, _name)
        return {
            "result": "success",
            "message": "User %s created group %s" % (operator.name, _name)
        }
    except Exception as e:
        return {
            "result": "fail",
            "message": "Generic error: " + str(e)
        }


def group_summary(groups):
    return list(gp.summary() for gp in groups)


def find_user(uid=None, email=None):
    if uid is None and email is None:
        return None
    if uid:
        return praat.User.query.get(uid)
    return praat.User.query.filter_by(email=email).first()



# retrieve or update group info
@app.route('/auth/groups/<gid>', methods=['GET', 'POST'])
#@login_required
def group_ops(gid):
    operator = g.user
    group = praat.Group.query.get(gid)
    if group is None:
        message = "Group %s does not exist" % (gid)
        return jsonify({
            "result": "fail",
            "message": message
            })
    if operator is None:
        operator = praat.User.query.first()
    if request.method == 'GET':
        return jsonify(group.details())

    allowed_actions = ['add', 'remove', 'transfer', 'setreader', 'seteditor']
    if not praat.is_owner(operator, group):
        message = "User %s has no permission to update group %s" % (operator.name, group.name)
        return jsonify({
            "result": "fail",
            "message": message
            })
    print "Request JSON!!!"
    print request.json
    action = request.json.get('action', '').lower()
    if not action in allowed_actions:
        message = "Invalid action %s" % (action)
        return jsonify({
            "result": "fail",
            "message": message
            })
    user = find_user(uid=request.json.get('userId'), email=request.json.get('userEmail'))
    if user is None:
        return jsonify({
            "result": "fail",
            "message": "Target user not found"
            })
    if action == 'add':
        resp = praat.add_user_to_group(operator, user, group)
    elif action == 'remove':
        resp = praat.remove_user_from_group(operator, user, group)
    elif action == 'transfer':
        resp = praat.transfer_group(operator, user, group)
    elif action == 'setreader':
        resp = praat.update_user_role(operator, user, group, 'reader')
    else:
        resp = praat.update_user_role(operator, user, group, 'editor')
    group = praat.Group.query.get(gid)
    resp['groupInfo'] = group.details();
    return jsonify(resp)


@app.route('/auth/annotations/<aid>', methods=['GET', 'PUT'])
@app.route('/auth/audios/<audio>/annotations/<aid>', methods=['GET', 'PUT'])
@login_required
def handle_single_annotation(aid, audio=None):
    annotation = praat.AudioAnnotation.query.get(aid)
    if annotation is None:
        return jsonify({"status": "fail", "message": "Annotation does not exist"})
    storage_svc = get_storage_service(praat.app.config)
    if request.method == 'GET':
        versions = storage_svc.show_versions(aid)
        resp = annotation.summary()
        resp['versions'] = versions
        return jsonify(resp)
    payload = request.json
    # save annotation details in annotation version
    attributes = {
        'created_by': g.user.email,
    }
    contents = {
        'comments': payload.get('comments', ''),
        'tierOne': payload.get('tierOne', ''),
        'tierTwo': payload.get('tierTwo', ''),
        'tierThree': payload.get('tierThree', ''),
    }
    storage_svc.put(aid, json.dumps(contents), attributes)
    annotation.updated_at = datetime.datetime.utcnow()
    praat.db_session.commit()
    return jsonify({"status": "success", "summary": annotation.summary()})

@app.route('/auth/annotations/<aid>/versions/<vid>/revert', methods=['POST'])
@login_required
def revert_annotation(aid, vid):
    storage_svc = get_storage_service(praat.app.config)
    attrs = {'created_by': g.user.email}
    resp = storage_svc.revert(aid, vid, attrs)
    return jsonify(resp)


@app.route('/auth/annotations/<aid>/versions/<vid>', methods=['GET'])
@app.route('/auth/audios/<audio>/annotations/<aid>/versions/<vid>', methods=['GET'])
@login_required
def annotation_version_handler(aid, vid, audio=None):
    storage_svc = get_storage_service(praat.app.config)
    result = storage_svc.get(aid, vid)
    if result is None:
        return jsonify({"status": "fail", "message": "Annotation version does not exist"})
    resp = result['version']
    try:
        resp.update(json.loads(result['data']))
    except:
        pass
    return jsonify(resp)


@app.route('/auth/audios/<audio>/annotations', methods=['GET', 'POST'])
@app.route('/auth/audios/<audio>/versions/<vid>/annotations', methods=['GET', 'POST'])
@login_required
def annotation_ops(audio, vid=None):
    user = g.user
    audio_obj = praat.Audio.query.get(audio)
    if audio_obj is None:
        return jsonify({"status": "fail", "message": "Audio file does not exist"})
    storage_svc = get_storage_service(praat.app.config)
    if request.method == 'GET':
        anns = []
        for annotation in audio_obj.annotations:
            summary = annotation.summary()
            if vid and vid != annotation.audio_version:
                continue
            if utils.is_true(request.args.get('show_versions')):
                summary['versions'] = storage_svc.show_versions(annotation.id)
            anns.append(summary)
        resp = {"status": "success", 'annotations': anns}
        return jsonify(resp)
    payload = request.json
    audio_version = vid or payload.get('audio_version')
    all_versions = storage_svc.show_versions(audio_obj.id)
    if audio_version is None:
        if len(all_versions) > 0:
            audio_version = all_versions[0]['version']
        else:
            return jsonify({"status": "fail", "message": "unable to find any version of audio"})
    else:
        version_exists = False
        for v in all_versions:
            if v['version'] == audio_version:
                version_exists = True
                break
        if not version_exists:
            return jsonify({"status": "fail", "message": "Audio version " + audio_version + " does not exist"})
    # Annotation key is a combinatiom of audio id, audio version, and annotation name
    name = payload['name']
    a_key_seed = "%s:%s:%s" % (audio, audio_version, name)
    # create or update an annotation object
    start_time = payload['startTime']
    end_time = payload['endTime']
    if float(start_time) < 0 or float(end_time) < float(start_time):
        return jsonify({"status": "fail", "message": "Invalid annotation start/end time"})
    annotation_obj = praat.AudioAnnotation.query.get(utils.generate_id(a_key_seed))
    if annotation_obj is None:
        print "Creating new Annotation"
        annotation_obj = praat.AudioAnnotation(name, audio, audio_version, start_time, end_time, a_key_seed)
        praat.db_session.add(annotation_obj)
        praat.db_session.commit()
    else:
        if annotation_obj.start_time != start_time or annotation_obj.end_time != end_time:
            return jsonify({"status":"fail", "message": "Inconsistent start time or end time for annotation " + name})
        annotation_obj.updated_at = datetime.datetime.utcnow()
        praat.db_session.commit()

    # save annotation details in annotation version
    attributes = {
        'created_by': user.email,
    }
    contents = {
        'commitMessage': payload.get('commitMessage', ''),
        'tierOne': payload.get('tierOne', ''),
        'tierTwo': payload.get('tierTwo', ''),
        'tierThree': payload.get('tierThree', ''),
    }
    storage_svc.put(annotation_obj.id, json.dumps(contents), attributes)
    return jsonify({"status": "success", "summary": annotation_obj.summary()})


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
    audio_obj = praat.Audio.query.get(audio)
    if audio_obj is None:
        return "Audio file not found"
    storage_svc = get_storage_service(praat.app.config)
    info = audio_obj.summary()
    info['versions'] = storage_svc.show_versions(audio_obj.id)
    return jsonify(info)

@app.route('/auth/audios/<aid>/versions/<vid>', methods=['GET'])
@login_required
def audio_version_handler(aid, vid):
    storage_svc = get_storage_service(praat.app.config)
    result = storage_svc.get(aid, vid)
    if result is None:
        return jsonify({"status": "fail", "message": "Audio version does not exist"})
    audio = praat.Audio.query.get(aid)
    resp = app.make_response(result['data'])
    resp.content_type = "audio/" + utils.fileType(audio.name)
    return resp


def generic_audio_ops(user, group, method, audio=None, params=None):
    if group is None:
        return "Group does not exist"
    storage_svc = get_storage_service(praat.app.config)
    if method == 'GET':
        #g_info = group.details()
        #return jsonify(g_info['details']['audios'])
        audios = []
        for audio in group.audios:
            info = audio.summary()
            if utils.is_true(params.get('show_versions')):
                info['versions'] = storage_svc.show_versions(audio.id)
            audios.append(info)
        resp = {"status": "success", "audios": audios}
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
        key_seed = group.id + audioName
        key = utils.generate_id(group.id + audioName)
        attrs = {
            'created_by': user.email,
        }
        audioObj = praat.Audio.query.get(key)
        retval = storage_svc.put(key, data, attrs)
        # save waveform
        temp_dir = '/tmp/waveform' + key + retval['version'] + '/'
        waveform_name = key + retval['version'] + '.png'
        utils.mkdir_p(temp_dir)
        with open(temp_dir + audioName, 'w') as fp:
            fp.write(data)
        script = praat._scripts_dir + 'drawWaveV2'
        params = [temp_dir + audioName, temp_dir + waveform_name]
        praat.runScript(script, params)
        with open(temp_dir + waveform_name, 'r') as fp:
            data = fp.read()
            attrs = {'name': audioName}
            attrs.update(retval)
            storage_svc.put(waveform_name, data, attrs)
        utils.rm_rf(temp_dir)

        if audioObj is None:
            print 'Creating new audio file'
            audioObj = praat.Audio(audioName, user, group, key_seed)
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
    #return jsonify(result)
    return redirect('/?context=workspace')

@app.route('/auth/audios/<aid>/versions/<vid>/waveform', methods=['GET'])
@login_required
def audio_waveform_handler(aid, vid):
    storage_svc = get_storage_service(praat.app.config)
    waveform_name = aid + vid + '.png'
    resp = app.make_response(storage_svc.get(waveform_name)['data'])
    resp.content_type = "image/png"
    return resp


@app.route('/auth/annotation_diff/<aid>/<rev1>/<rev2>', methods=['GET'])
# compute the diff between rev1 and rev2 off annotation aid
def annotation_diff(aid, rev1, rev2):
    storage_svc = get_storage_service(praat.app.config)
    revision1 = storage_svc.get(aid, rev1)
    revision2 = storage_svc.get(aid, rev2)
    if revision1 is None or revision2 is None:
        return jsonify({"status": "fail"})
    # we have commitMessage, tierOne, tierTwo, tierThree in revision data
    rev1_data = json.loads(revision1['data'])
    rev2_data = json.loads(revision2['data'])
    diff = {
        'revision': calc_diff(rev1, rev2, 'revision'),
        'commitMessage': calc_diff(rev1_data['commitMessage'], rev2_data['commitMessage'], 'commitMessage'),
        'tierOne': calc_diff(rev1_data['tierOne'], rev2_data['tierOne'], 'tierOne'),
        'tierTwo': calc_diff(rev1_data['tierTwo'], rev2_data['tierTwo'], 'tierTwo'),
        'tierThree': calc_diff(rev1_data['tierThree'], rev2_data['tierThree'], 'tierThree'),
    }
    return jsonify(diff)


def calc_diff(data1, data2, filename):
    lines1 = data1.split("\n")
    lines2 = data2.split("\n")
    return "\n".join(difflib.unified_diff(lines1, lines2, fromfile=filename, tofile=filename, lineterm=''))
