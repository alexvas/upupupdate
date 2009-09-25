# -*- coding: utf-8 -*-
from datetime import time
from django.db.models import signals
from google.appengine.ext import db
from ragendja.dbutils import cleanup_relations, KeyListProperty

from teammail import dating

ALL = 1000
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%A, %B %d, %Y at " + TIME_FORMAT
DATE_FORMAT = "%A, %B %d, %Y"
ALT_DATE_FORMAT = '%m/%d/%y'
MAILING_DEADLINE = dating.embedLocalTimezone(time(0, 1))



class Logged(db.Model):
    changed_by = db.UserProperty(("who changed"), auto_current_user=True)
    last_changed = db.DateTimeProperty(("when changed"), auto_now=True)
    added_by = db.UserProperty(("who added"), auto_current_user_add=True)
    added_date = db.DateTimeProperty(("when added"), auto_now_add=True)


    
class Team(Logged):
    name = db.StringProperty(required=True)
    is_active = db.BooleanProperty(('is active'), default=True)
    admins = db.StringListProperty()

    def __unicode__(self):
        return self.name

signals.pre_delete.connect(cleanup_relations, sender=Team)



class Division(Logged):
    name = db.StringProperty(required=True)
    team = db.ReferenceProperty(Team, required=True)

    def __unicode__(self):
        return self.name



class Contact(Logged):
    name = db.StringProperty()
    is_active = db.BooleanProperty(('is active'), default=True)
#    team = db.ReferenceProperty(Team, required=True)
    email = db.EmailProperty(required=True)
    teams = KeyListProperty(Team)
#    division = KeyListProperty(Division)

    def __unicode__(self):
        if self.name:
            return u"%s <%s>" % (self.name, self.email)
        else:
            return self.email       



class Report(Logged):
    contact = db.ReferenceProperty(Contact, required=True)
    body = db.TextProperty(required=True)

    def __unicode__(self):
        return "%s's report" % self.contact


        
class Template(Logged):
    name = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    team = db.ReferenceProperty(Team, required=True)

    def __unicode__(self):
        return self.name
