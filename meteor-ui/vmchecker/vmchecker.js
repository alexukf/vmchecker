"use strict";

var Courses = new Meteor.Collection("courses");
var Assignments = new Meteor.Collection("assignments");
var Grades = new Meteor.Collection("grades");
var Results = new Meteor.Collection("results");

// Restricts creating accounts on the client
Accounts.config({
  forbidClientAccountCreation: true
});

if (Meteor.isClient) {

  Deps.autorun(function() {
    Meteor.subscribe("courses");
    Meteor.subscribe("assignments");
    Meteor.subscribe("grades");
    Meteor.subscribe("userData");
    Meteor.subscribe("results");
  });

  var initializedCursor = false;

  Deps.autorun( function() {
    if ( typeof Session.get("courseCursor") == 'undefined' ) {

      Session.set("courseCursor" , Courses.findOne({}, {
        sort: {
          id: -1,
          title: 1
        }
      }));

      if ( typeof Session.get("courseCursor") != 'undefined' ) {

        Session.set("courseId", Session.get("courseCursor").id );
        Meteor.call('getAssignments', Session.get("courseId"));
        Meteor.call('getAllGrades', Session.get("courseId"));
      }
    } else if ( ! initializedCursor ) {
      Session.set("courseId", Session.get("courseCursor").id );
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
      initializedCursor = true;
    }
  });

  Template.courses.courses = function() {
    return Courses.find({}, {
      sort: {
        id: -1,
        title: 1
      }
    });
  };

  Template.courses.events({
    'change': function(event) {
      var elem = event.currentTarget;
      Session.set("courseId", elem.value);
      Meteor.call('getAssignments', Session.get("courseId"));
      Meteor.call('getAllGrades', Session.get("courseId"));
      Session.set("courseCursor",  Session.get("courseId"));
    },
    'click': function(event) {
      var elem = event.currentTarget;
      Meteor.call('getCourses');
      if (Session.get("courseId") != elem.value) {
        Session.set("courseId", elem.value);
        Meteor.call('getAssignments', Session.get("courseId"));
        Meteor.call('getAllGrades', Session.get("courseId"));
        Session.set("courseCursor",  Session.get("courseId"));
      }
    }
  });

  Template.changeLang.events({
    'change': function(event) {
      if (Cookie.get("i18next") != event.currentTarget.value) {
        Cookie.set("i18next", event.currentTarget.value);
        history.go(0);
      }
    }
  });

  Template.changeLang.languages = function() {
    // TODO: use database maybe?
    return [{
      "code": "ro",
      "name": "Romana",
      "selected": (Cookie.get('i18next') == "ro" ? "selected" : "")
    }, {
      "code": "en",
      "name": "English",
      "selected": (Cookie.get('i18next') == "en" ? "selected" : "")
    }];
  }

  Template.assignments.assignments = function() {
    return Assignments.find({
      courseId: Session.get("courseId")
    });
  };

  Template.assignments.events({
    'click': function(event) {
      var text = event.currentTarget.id;
      Session.set("assignmentId", text.trim());
      Meteor.call(
        'getUserResults',
        Session.get('courseId'),
        Session.get('assignmentId'),
        Meteor.user().username
      );
      console.log("---" + Session.get("assignmentId"));
    }
  });


  Template.assignmentInfo.content = function() {
    return Assignments.find({
      courseId: Session.get("courseId"),
      assignmentId: Session.get("assignmentId")
    });
  }

  Template.grades.grades = function() {
    return Grades.find({
      courseId: Session.get("courseId")
    }, {
      sort: {
        studentId: -1
      },
      limit: 10
    });
  }

  Template.grades.display = function() {
    return Session.get("assignmentId") == "";
  }

  Template.result.content = function() {
    if (Meteor.user()) {

      if (! Session.get('courseId') || ! Session.get('assignmentId'))
        return "";

      var val = Results.findOne({
        courseId: Session.get('courseId'),
        assignmentId: Session.get('assignmentId'),
        userId: Meteor.user().username
      }).content;

      var replaceValue = /\\n/g;
      val = val.replace( replaceValue, "%%");

      var parsed = JSON.parse(val);
      var result = "";

      for ( var field in parsed ) { 
        for ( var element in parsed[field] ) {
          result += element + parsed[field][element];
        }
      }

      replaceValue = /%%/g;
      result = result.replace( replaceValue, "<br />");  

      return result;
      return JSON.stringify(parsed);
    }
    return "";
  }

  Template.circle.display = function(league) {
    return Session.get("loading") == true;
  };

  Template.upload.events({
    'change input': function(ev) {
      _.each(ev.target.files, function(file) {
        Meteor.saveFile(file);
        //Meteor.call('saveFile', file, Session.get('courseId'), Session.get('assignmentId'));
      });
    }
  });
}


if (Meteor.isServer) {
  //Meteor.users.remove({});
  Meteor.startup(function() {
    console.log("Started server");

    Meteor.publish("grades", function() {
      return Grades.find({});
    });
    Meteor.publish("courses", function() {
      return Courses.find({});
    });
    Meteor.publish("assignments", function() {
      return Assignments.find({});
    });
    // Meteor.publish("userData", function () {
    //   return Meteor.users.find({});
    // });
    Meteor.publish("results", function() {
      return Results.find({});
    });

    /// ===>>> SERVER METHODS

    // the result from calling getCourses
    var getCoursesStaticResults;

    // last update time
    var getCoursesLastUpdateTime = 0;

    /// Time in Miliseconds
    var getCoursesTimeTreshold = 6000;

    Meteor.methods({
      getCourses: function() {
        this.unblock();
        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }

        // the code only calls the getCourses method on the server only if an amount of time has elapsed from the last call
        // the amount of time is specified by the $getCoursesLastUpdateTime variable
        var currentTime = (new Date()).getTime();
        console.log("---Current Time:" + currentTime);
        console.log("---LastTime:" + getCoursesLastUpdateTime);
        console.log("---Difference:" + (currentTime - getCoursesLastUpdateTime));

        if ( typeof getCoursesStaticResults === 'undefined' || currentTime - getCoursesLastUpdateTime > getCoursesTimeTreshold ) {
          console.log("Query to Boss");
          getCoursesStaticResults = HTTP.get("http://localhost/services/services.py/getCourses?null", options);
          getCoursesLastUpdateTime = currentTime;

          var res = getCoursesStaticResults;

          var names = JSON.parse(res.content);
          console.log(names);
          //Courses.remove({});
          for (var i = 0; i < names.length; i++) {
            Courses.update({
              id: names[i].id
            }, {
              id: names[i].id,
              title: names[i].title
            }, {
              upsert: true
            });
        }
        }
      },
      getAssignments: function(courseId) {
        this.unblock();
        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getAssignments?courseId=" + courseId, options);

        var assignments = JSON.parse(res.content);
        for (var i = 0; i < assignments.length; i++) {
          Assignments.update({
            courseId: courseId,
            assignmentId: assignments[i].assignmentId
          }, {
            courseId: courseId,
            assignmentId: assignments[i].assignmentId,
            assignmentTitle: assignments[i].assignmentTitle,
            deadline: assignments[i].deadline,
            statementLink: assignments[i].statementLink,
            assignmentStorage: assignments[i].assignmentStorage
          }, {
            upsert: true
          });
        }
      },
      getAllGrades: function(courseId) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getAllGrades?courseId=" + courseId, options);
        var students = JSON.parse(res.content);
        for (var i = 0; i < students.length; i++) {
          for (var assignmentId in students[i].results) {
            Grades.update({
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId
            }, {
              courseId: courseId,
              studentId: students[i].studentId,
              assignmentId: assignmentId,
              grade: students[i].results[assignmentId]
            }, {
              upsert: true
            });
          }
        }
      },
      getUserResults: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getUserResults?courseId=" +
          courseId + "&assignmentId=" + assignmentId + "&username=" + username, options);

        var value = res.content;
        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });

      },
      getUserUploadedMd5: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getUploadedMd5?courseId=" +
          courseId + "&assignmentId=" + assignmentId, options);
        var value = res.content;

        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });
      },
      getUserStorageDirContents: function(courseId, assignmentId, username) {
        this.unblock();

        if (this.userId == null)
          return;

        var key = Meteor.users.findOne({
          _id: this.userId
        }).profile.pysid;
        var options = {
          headers: {
            Cookie: "pysid=" + key
          }
        }
        var res = HTTP.get("http://localhost/services/services.py/getStorageDirContents?courseId=" +
          courseId + "&assignmentId=" + assignmentId, options);
        var value = res.content;

        Results.upsert({
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username
        }, {
          courseId: courseId,
          assignmentId: assignmentId,
          userId: username,
          content: value
        });
      }
    });

    /// <<<=== END SERVER METHODS

  });
}
