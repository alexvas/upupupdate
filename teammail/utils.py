from teammail import models
from teammates import users

def get_team(request):
    if request:
        user = request.user
    if not (user and user.is_authenticated):
        return None
    nickname = user.username
    return users.Team.all().filter('is_active', True).filter("admins", nickname).get(); 


def get_active_teams():
    return users.Team.all().filter('is_active', True).order("name").fetch(models.ALL); 


def get_team_choices():
    active = get_active_teams()
    return map(lambda x: (str(x.key()), x.name), active) 


def get_users(team):
    return users.User.all().filter("is_active", True).filter('teams', team).order("name").fetch(models.ALL)    


def get_all_users(team):
    return users.User.all().filter('teams', team).order("name").fetch(models.ALL)    
