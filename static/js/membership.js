function createGroupListItem(group, groupListener) {
    var liNode = document.createElement('li');
    var aNode = document.createElement('a');
    aNode.setAttribute('id', group.id);
    aNode.innerHTML = group.name;
    aNode.onclick = groupListener;
    liNode.append(aNode);
    return liNode;
}

function populateGroupList(groups) {
    var gList = $('#groupList');
    gList.empty();
    var gListener = function() {
        console.log("Listening groups");
        console.log(this.id);
        getGroupInfo(this.id, showGroup);
    };
    $.each(groups, function(index, _group) {
        gList.append(createGroupListItem(_group, gListener));
    });
}

function getGroupInfo(gid, callback) {
    var api = '/auth/groups/' + gid;
    var gh = $('#groupHolder');
    console.log("Group Holder ");
    console.log(gh);
    gh.val(gid);
    console.log("Set Group Holder ");
    $.get(api, function(data) {
        console.log("Groups");
        console.log(data);
        callback(data);
    });
}

function showGroup(gInfo) {
    var groupNameNode = $("#groupName");
    var groupOwnerNode = $("#groupOwner");
    var groupMembersNode = $("#groupMembers");
    groupMembersNode.empty();
    groupNameNode.text(gInfo.name);
    groupOwnerNode.text(gInfo.ownerName + ' (' + gInfo.ownerEmail + ')');
    $.each(gInfo.details.members, function(index, member) {
        groupMembersNode.append(createGroupMemberNode(member));
    });
    var btn = $('#selectBtn');
    btn.off('click').click(
        simplePost('/auth/profile', JSON.stringify({groupId: gInfo.id}), function(d) {
            location.href = '/?context=workspace';
        })
    );
}

function createGroupMemberNode(member) {
    //<li>One : <input type='radio' name='one' value='reader'>reader <input type='radio' name='one' value='editor'>editor </li>
    var memberInfo = basicUserInfo(member) + " --- " + roleHtml(member.role);
    var node = document.createElement('li');
    node.id = member.id;
    console.log(memberInfo);
    node.innerHTML = memberInfo;
    return node;
}

function basicUserInfo(user) {
    return "<b>" + user.name + "</b> (" + user.email + ")";
}

function roleHtml(role) {
    var r = role.toUpperCase();
    if (r == 'READER') {
        return  "<font color='green'>" + r + "</font>";
    } else {
        return  "<font color='red'>" + r + "</font>";
    }
}

function simplePost(api, payload, callback) {
    return function() {
        console.log("Posting to API " + api + " with payload " + payload);
        $.ajax({
            type: "POST",
            url: api,
            data: payload,
            contentType: "application/json",
            dataType: "text",
            success: function(_data) {
                console.log("success data ");
                console.log(_data);
                callback(_data);
            },
            error: function(_data) {
                console.log("error data ");
                console.log(_data);
                callback(_data);
            }
        });

    };
}
