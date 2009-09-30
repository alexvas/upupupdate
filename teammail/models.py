# -*- coding: utf-8 -*-
from datetime import time
from google.appengine.ext import db

from teammail import dating
from teammates import users

ALL = 1000
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%A, %B %d, %Y at " + TIME_FORMAT
DATE_FORMAT = "%A, %B %d, %Y"
ALT_DATE_FORMAT = '%m/%d/%y'
MAILING_DEADLINE = dating.embedLocalTimezone(time(0, 1))



class Report(users.Logged):
    user = db.ReferenceProperty(users.User, required=True)
    team = db.ReferenceProperty(users.Team, required=True)
    body = db.TextProperty(required=True)

    def __unicode__(self):
        return "%s's report" % self.user


        
class Template(users.Logged):
    name = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    team = db.ReferenceProperty(users.Team, required=True)

    def __unicode__(self):
        return self.name
