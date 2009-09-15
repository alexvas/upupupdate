from teammail import models

def get_team(request):
    if request:
        user = request.user
    if not (user and user.is_authenticated):
        return None
    nickname = user.username
    return models.Team.all().filter('is_active', True).filter("admins", nickname).get(); 
