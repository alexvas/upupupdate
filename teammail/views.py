# -*- coding: utf-8 -*-
from HTMLParser import HTMLParser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from teammail import models, forms, mail, utils
from teammates import users
import email
import re



def main(request):
    return render_to_response(
        request,
        'teammail/main.html',
        )


def _get_active_teams():
    return users.Team.all().filter('is_active', True).fetch(models.ALL)


def invitation(request):
    for team in _get_active_teams():
        mail.invitation(request, team)
    return HttpResponse()


def digest(request):
    for team in _get_active_teams():
        mail.digest(request, team)
    return HttpResponse()

    
def empty(request):
    return HttpResponse()


class QuoteRemover(HTMLParser):
    
    def __init__(self):
        self.reset()        
        self.out = ''
        self.quotation = False


    def _add_start_tag(self, tag, attrs, slash=False):
        if slash:
            e = '/>'
        else:
            e = '>'

        self.out += '<' + tag
        
        if not attrs:
            self.out += e
            return 

        self.out += ' '
        
        ats = []
        for pair in attrs:
            ats.append("%s='%s'" % (pair[0], pair[1]))
        
        self.out += ' '.join(ats)
        self.out += e
        

    def _has_attr(self, attrs, key, value): 
        for pair in attrs:
            if key == pair[0] and value == pair[1]:
                return True
        return False


    def handle_starttag(self, tag, attrs):
        if self.quotation:
            return
        if tag == 'div':
            self.quotation = self._has_attr(attrs, 'class', 'gmail_quote')
            if self.quotation:
                return
        elif tag == 'tr':
            self.quotation = self._has_attr(attrs, 'class', 'upupupdate_quote')
            if self.quotation:
                return
        self._add_start_tag(tag, attrs, slash=False)
        
        
    def handle_startendtag(self, tag, attrs):
        if self.quotation:
            return
        self._add_start_tag(tag, attrs, slash=True)


    def handle_endtag(self, tag):
        if self.quotation:
            return
        self.out += "</%s>" % tag
        

    def handle_data(self, data):
        if not self.quotation:
            self.out += data


def get_charset(message, default="ascii"):
    """Get the message charset"""

    if message.get_content_charset():
        return message.get_content_charset()

    if message.get_charset():
        return message.get_charset()

    return default


def incoming(request):
    message = email.message_from_string(request.raw_post_data);
#    import logging
    
    plain = u''
    html = u''
    fr = u''
    to = u''
    message_charset = get_charset(message) 
    
    for p in message.walk():
        charset = get_charset(p, message_charset)
        if ('text/plain' == p.get_content_type()):
            plain = unicode(p.get_payload(decode=True), charset)
        elif ('text/html' == p.get_content_type()):
            html = unicode(p.get_payload(decode=True), charset)
        f = p.get('from')
        t = p.get('to')
        if not fr and f: fr = unicode(f, charset)
        if not to and t: to = unicode(t, charset)
    
    body = html or plain
    
    if not (body and fr and to):
        raise Exception("dummy message received: %s" % message)
    
    if '<' in fr and '>' in fr:
        fr = re.sub(r'^[^<]*<([^>]+)>.*$', r'\1', fr)
    user = users.User.all().filter('is_active', True).filter('email', fr).get()
    
    if not user:
        raise Exception("no user for incoming mail from '%s'" % fr)
    
    team = None
    for t in user.teams:
        t = users.Team.get(t)
        if not t or not t.is_active:
            continue
        if t.name in to:
            team = t
            break
    
    if not team:
        raise Exception("no team for incoming mail from '%s'" % fr)

    if html:
        quote_remover = QuoteRemover()
        quote_remover.feed(html)
        quote_remover.close()          
        body = quote_remover.out

    quotation_position = body.find(mail.QUOTATION)
    if quotation_position > -1:
        body = body[:quotation_position]

    models.Report(user=user, team=team, body=body).put()
    return HttpResponse()


def create_admin_user(request):
    user = users.User.get_by_key_name('admin')
    if not user or user.username != 'admin' or not (user.is_active and
            user.is_staff and user.is_superuser and
            user.check_password('admin')):
        user = users.User(key_name='admin', email='admin@localhost.org', name='Boss Admin',
            is_active=True, is_staff=True, is_superuser=True)
        user.set_password('adminno')
        user.put()
    return HttpResponse()

def _embed_application_admin_user_list_forms(users, request=None):
    for user in users:
        if request:
            user.form = forms.AppAdminUserListEntry(request.POST, prefix=unicode(user.key()), auto_id=False) 
        else:
            user.form = forms.AppAdminUserListEntry(prefix=unicode(user.key()), auto_id=False)


def _embed_application_admin_team_list_forms(teams, request=None):
    for team in teams:
        if request:
            team.form = forms.AppAdminTeamListEntry(request.POST, prefix=unicode(team.key()), auto_id=False) 
        else:
            team.form = forms.AppAdminTeamListEntry(prefix=unicode(team.key()), auto_id=False) 


def update_team_set(user, teams):
    was = set(user.teams)
    _is = set(teams)
    if was != _is:
        user.teams = _is
        user.put()


@staff_only
def app_admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    _users = users.User.all().filter("is_active", True).order("name").fetch(models.ALL)
    teams = users.Team.all().filter("is_active", True).order("name").fetch(models.ALL)
    for team in teams:
        team.users = utils.get_users(team)    

    formAddTeam = None
    formAddUser = None
    
    action = None
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST['action']

    add_user_to_team = None
    if request.method == 'POST' and 'add_user_to_team' in request.POST:
        add_user_to_team = request.POST['add_user_to_team']
    
    if add_user_to_team:
        num = add_user_to_team.split('_')[1]
        num = int(num)
        team = teams[num]
        email = request.POST[add_user_to_team]
        email = re.sub(r'^[^<]*<([^>]+)>.*$', r'\1', email)
        user = users.User.all().filter("email", email).filter("is_active", True).get()
        if user:
            user.teams.append(team.key())
            user.put()
                    
        return HttpResponseRedirect(request.get_full_path())

    elif 'add_team' == action:
        formAddTeam = forms.AppAdminAddTeam(request.POST)
        
        if formAddTeam.is_valid():
            cleaned_data = formAddTeam.cleaned_data
            users.Team(name=cleaned_data['name']).put()
            return HttpResponseRedirect(request.get_full_path())

    elif 'inactivate_teams' == action:
        _embed_application_admin_team_list_forms(teams, request)

        valid = True
        for team in teams:
            if not team.form.is_valid():
                valid = False
                continue
            
        if valid:
            for team in teams:
                cleaned_data = team.form.cleaned_data
                if cleaned_data['flag'] == u'on':
                    team.is_active = False
                    team.put()
            return HttpResponseRedirect(request.get_full_path())
        
    elif 'add_user' == action:
        formAddUser = forms.AppAdminAddUser(request.POST)
        
        if formAddUser.is_valid():
            cleaned_data = formAddUser.cleaned_data

            email = cleaned_data['email']
            user = users.User.objects.create_user(email, email)
            
            teams = users.Team.get(cleaned_data['teams'])
            if teams:
                teams = filter(lambda x: x, teams)
                teams = map(lambda x: x.key(), teams)
            
            if teams:
                user.teams = teams
                
            name = cleaned_data['name']
            if name:
                user.name = name

            user.put()
            from registration.utils import password_reset
            password_reset(request, user, creation=True)
            return HttpResponseRedirect(request.get_full_path())
        
    elif 'assign_teams_to_users' == action:
        _embed_application_admin_user_list_forms(_users, request)
        
        valid = True
        for user in _users:
            if not user.form.is_valid():
                valid = False
                continue
            cleaned_data = user.form.cleaned_data
            update_team_set(user, cleaned_data['teams'])
            
        if valid:
            return HttpResponseRedirect(request.get_full_path())
        
    elif 'inactivate_users' == action:
        _embed_application_admin_user_list_forms(_users, request)

        valid = True
        for user in _users:
            if not user.form.is_valid():
                valid = False
                continue
            
        if valid:
            for user in _users:
                cleaned_data = user.form.cleaned_data
                if cleaned_data['flag'] == u'on':
                    user.is_active = False
                    user.put()
            return HttpResponseRedirect(request.get_full_path())
            

    if not formAddTeam:
        formAddTeam = forms.AppAdminAddTeam()

    if not formAddUser:
        formAddUser = forms.AppAdminAddUser()
        
    if teams and not 'form' in dir(teams[0]):
        _embed_application_admin_team_list_forms(teams)
        
    if _users and not 'form' in dir(_users[0]):
        _embed_application_admin_user_list_forms(_users)

    return render_to_response(request,
                              'teammail/app_admin_dashboard.html',
                              data={
        'formAddTeam': formAddTeam,
        'formAddUser': formAddUser,
        'teams': teams,
        'users': _users,
    })
    
    
@login_required
def fork(request):
    if request.user.is_superuser:
        return HttpResponseRedirect('/dashboard/');
    else:
        return HttpResponseRedirect('/manage/teammail/');
