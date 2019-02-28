$(document).ready(function() {
          console.log("Document ready!");
          $.get('/auth/profile', function(data) {
              console.log("logined in user:" + data.name + data.email);
	      showMembership();
           });
 });

	function showMembership() {
          console.log("Show membership");
          $.get('/auth/profile', function(data) {
              console.log(data.name, data.email);
              populateGroupList(data.details.membership, 'membership');
              showGroupInfo(data.currentGroupId, 'membership');
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
              showActions(gid);
          });
      }


	function showActions(gid) {
    		$("#actionItems").show();
    		var details = $("#actionDetails");
    		details.val();
 		var btn = $("#selectBtn");
    		btn.text("Submit");
	}

	function extractGroupMembers(members) {
          var memberList = [];
          for (var index = 0; index < members.length; index++) {
              memberList.push( members[index].name + "(" + members[index].email + ")" );
          }
          return memberList;
      }

