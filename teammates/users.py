from google.appengine.ext import db
from ragendja.auth.models import User as DjangoUser
from ragendja.dbutils import KeyListProperty

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


class User(DjangoUser):
    teams = KeyListProperty(Team)
    name = db.StringProperty()    

    @property
    def username(self):
        return self.email

    @property
    def first_name(self):
        if not self.name:
            return ''
        if not ' ' in self.name:
            return self.name
        (first, last) = self.name.rsplit(None, 1)
        if first:
            return first
        return ''
        
    @property
    def last_name(self):
        if not self.name:
            return ''
        if not ' ' in self.name:
            return ''
        (first, last) = self.name.rsplit(None, 1)
        if last:
            return last
        return ''
    
    def get_full_name(self):
        return self.name

    def __unicode__(self):
        if self.name:
            name = self.name
        else:
            name = 'No name'
            
        return "%s <%s>" % (name, self.email)



