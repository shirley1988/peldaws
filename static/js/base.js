
	$(document).ready(function() {
          console.log("Document ready!");
          $.get('/auth/profile', function(data) {
              console.log(data);
              var userName = data.name;
              var currentGroupName = data.details.currentGroup.name;
              $("#operatorHolder").val(data.id);
              $("#groupHolder").val(data.details.currentGroup.id);
              
	      var context = $("#contextHolder").val()
              if (context == 'ownership') {
                  showOwnership();
              } else if (context == 'membership') {
                  showMembership();
              } else {
		  showWorkspace();
	      }
          });
      });

	function showWorkspace() {
          console.log("Show workspace");
          $.get('/auth/profile', function(data) {
              console.log(data);
              populateGroupList(data.details.membership, 'membership');
              $("#groupDisplay").hide();
              var audiofile = $('#audioHolder').val();
              $('#waveformImg').prop('src', "/waveform/" + audiofile);
              $('#waveformImg').load();
              $('#audioPlayer').prop('src', "/play/" + audiofile);
              $('#audioPlayer').load();
              $("#workspace").show();
          });
        }

function zoomImage(dir) {
    var img = $('#waveformImg');
    var w = img.width();
    var h = img.height();
    console.log("Current size: W " + img.width() + " H " + img.height());
    var inFactor = 0.8;
    var outFactor = 1.25;
    if (dir > 0) {
        console.log("Zoom out image");
        img.width(w * outFactor);
        img.height(h * outFactor);
    } else {
        console.log("Zoom in image");
        img.width(w * inFactor);
        img.height(h * inFactor);
    }
    console.log("New size: W " + img.width() + " H " + img.height());
}

	function showMembership() {
          console.log("Show membership");
          $.get('/auth/profile', function(data) {
              console.log(data);
              populateGroupList(data.details.membership, 'membership');
              $("#workspace").hide();
              showGroupInfo(data.currentGroupId, 'membership');
          });
      }


	function showOwnership() {
          console.log("Show ownership");
          $.get('/auth/profile', function(data) {
              console.log(data);
              populateGroupList(data.details.ownership, 'ownership');
              $("#workspace").hide();
              showGroupInfo(data.details.ownership[0].id, 'ownership');
          });
        }

	 function populateGroupList(groups, context) {
          var gList = $('#groupList');
          gList.empty();
          $.each(groups, function(index, _group) {
              gList.append(createGroupListItem(_group, context));
		console.log("polulating each group");
          });
         }

	 function createGroupListItem(group, context) {
          var liNode = document.createElement('li');
          var aNode = document.createElement('a');
          aNode.setAttribute('id', group.id);
          aNode.innerHTML = group.name;
          aNode.onclick = function() {
              showGroupInfo(group.id, context);
          };
          liNode.append(aNode);
          return liNode;
      }

      function showGroupInfo(gid, context) {
          console.log("Group " + gid + "was just clicked");
          $("#groupHolder").val(gid);
          var groupNameNode = $("#groupName");
          var groupOwnerNode = $("#groupOwner");
          var groupMembersNode = $("#groupMembers");
          var api = '/auth/groups/' + gid;
          $.get(api, function(data) {
              //console.log("Group data for " + gid);
              //console.log(data);
              groupNameNode.text(data.name);
              groupOwnerNode.text(data.ownerName);
              var members = extractGroupMembers(data.details.members);
              groupMembersNode.text(members.join(", "));
              $("#groupDisplay").show();
	      if (context == 'ownership') {
                  showActions(gid);
              } else {
                  enableSwitchButton(gid);
              }
          });
      }


	function updateAnimation() {
    var player = document.getElementById('audioPlayer');
    console.log("Duration: " + player.duration);
    console.log("Current time: " + player.currentTime);
    var percent = Math.round(player.currentTime * 88 / player.duration);
    var newPos = 6 + percent;
    console.log("New relative position: " + newPos + "%");
    $('#progressLine').text(player.currentTime);
    $('#progressLine').css("left", newPos + "%");
}

function resetAnimation() {
    $('#progressLine').text("");
    $('#progressLine').css("left", "6%");
}

function showProgress() {
    $('#progressLine').show();
}


	function validateAction() {
    var parts = $("#actionDetails").val().split(",");
    console.log(parts);
    var btn = $("#selectBtn");
    if (parts.length != 2) {
        console.log("Invalid action string");
        btn.attr('disabled', true);
        return false;
    }
    var email = parts[1].toLowerCase().trim();
    if (email.includes(" ") ) {
        console.log("Invalid email address " + email);
        btn.attr('disabled', true);
        return false;
    }
    var act = parts[0].trim().toLowerCase();
    if (act == 'add' || act == 'remove' || act == 'transfer') {
        btn.attr('disabled', false);
        var payload =  JSON.stringify({
            action: act,
            userEmail: email
        });
        btn.off('click').click(
            simplePost('/auth/groups/' + $("#groupHolder").val(),  payload, function(d) {
                showOwnership();
            })
        );
        return;
    }
    console.log("Invalid actions");
    btn.attr('disabled', true);
    return false;
}

	function showActions(gid) {
    		$("#actionItems").show();
    		var details = $("#actionDetails");
    		details.val();
 		var btn = $("#selectBtn");
    		btn.text("Submit");
	}

	function saveAnnotation() {
    var name = $('#annotationName').val();
    var startTime = $('#startTime').val();
    var endTime = $('#endTime').val();
    var tierOne = $('#tierOne').val();
    var tierTwo = $('#tierTwo').val();
    var tierThree = $('#tierThree').val();
    var payload = {
        sound: $('#audioHolder').val(),
        name: name,
        startTime: startTime,
        endTime: endTime,
        tierOne: tierOne,
        tierTwo: tierTwo,
        tierThree, tierThree
    }
    console.log(payload);
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


	function enableSwitchButton(gid) {
          $("#actionItems").hide();
          var btn = $("#selectBtn");
          btn.text("Select to work");
          btn.off('click').click(
              simplePost('/auth/profile', JSON.stringify({groupId: gid}), function(d) {
                  location.href = '/?context=workspace';
              })
          );
        }


	function extractGroupMembers(members) {
          var memberList = [];
          for (var index = 0; index < members.length; index++) {
              memberList.push( members[index].name + "(" + members[index].email + ")" );
          }
          return memberList;
      }


