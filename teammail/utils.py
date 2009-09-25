from teammail import models

def get_team(request):
    if request:
        user = request.user
    if not (user and user.is_authenticated):
        return None
    nickname = user.username
    return models.Team.all().filter('is_active', True).filter("admins", nickname).get(); 


def get_active_teams():
    return models.Team.all().filter('is_active', True).order("name").fetch(models.ALL); 


def get_team_choices():
    return map(lambda x: (str(x.key()), x.name), get_active_teams()) 


def get_contacts(team):
    return models.Contact.all().filter("is_active", True).filter('teams', team).order("name").fetch(models.ALL)    
 
