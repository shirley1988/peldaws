from flask import send_from_directory
from flask import g, jsonify, request
from praat import app
import praat
import utils
from flask_login import login_required


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
# TODO: require login
#@login_required
def groups():
    operator = g.user
    if operator is None:
        operator = praat.User.query.first()
    if request.method == 'GET':
        res = {
            'ownership': group_summary(operator.ownership),
            'membership': group_summary(operator.membership),
        }
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
# TODO: require login
#@login_required
def group_ops(gid):
    operator = g.user
    group = praat.Group.query.get(gid)
    if group is None:
        return "Group %s does not exist" % (gid)
    if operator is None:
        operator = praat.User.query.first()
    if request.method == 'GET':
        return jsonify(group.details())
    #if request.method == 'DELETE':
    #    praat.delete_group(operator, group)
    #    return "User %s just deleted group %s" % (operator.name, group.name)
    else:
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
