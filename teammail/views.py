# -*- coding: utf-8 -*-
import email, re

from HTMLParser import HTMLParser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden

from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from teammail import models, forms, mail, utils
from teammates import users


def main(request):
    return render_to_response(
        request,
        'teammail/main.html',
        )


def invitation(request):
    for team in utils.get_active_teams():
        mail.invitation(request, team)
    return HttpResponse()


def digest(request):
    for team in utils.get_active_teams():
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


def _embed_application_admin_team_assign_user_forms(teams, request=None):
    for team in teams:
        if request:
            team.assign_form = forms.AppAdminAssignUserToTeamOrCreateThem(request.POST, prefix=unicode(team.key()), auto_id="%s") 
        else:
            team.assign_form = forms.AppAdminAssignUserToTeamOrCreateThem(prefix=unicode(team.key()), auto_id="%s") 


def update_team_set(user, teams):
    was = set(user.teams)
    _is = set(teams)
    if was != _is:
        user.teams = _is
        user.put()


def _create_user(request, email, name, teams):
    user = users.User.objects.create_user(email, email)

    if name:
        user.name = name
            
    if teams:
        user.teams = teams
                
    user.put()
    from registration.utils import password_reset
    password_reset(request, user, creation=True)
    return user


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
        _embed_application_admin_team_assign_user_forms(teams, request)
        valid = True
        for team in teams:
            form = team.assign_form
                        
            if not form.is_valid():
                valid = False
            
        if valid:
            for team in teams:
                form = team.assign_form
                f = form.fields['team']
                if f.user:
                    f.user.teams.append(team.key())
                    f.user.put()
                    return HttpResponseRedirect(request.get_full_path())
                if f.email:
                    _create_user(request, f.email, f.name, [team])
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
            name = cleaned_data['name']
            teams = users.Team.get(cleaned_data['teams'])
            if teams:
                teams = filter(lambda x: x, teams)
                teams = map(lambda x: x.key(), teams)

            _create_user(request, email, name, teams)
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
        
    if teams: 
        if not 'form' in dir(teams[0]):
            _embed_application_admin_team_list_forms(teams)
        if not 'assign_form' in dir(teams[0]):
            _embed_application_admin_team_assign_user_forms(teams)
        
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


def change_entity(request, key, form_class):
    instance = get_object_or_404(form_class.Meta.model, key) 
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = form_class(instance=instance)
    return render_to_response(request, 'teammail/change_entity.html', data={ 'form': form, })


def app_admin_dashboard_user_edit(request, key):
    return change_entity(request, key, forms.User)


def app_admin_dashboard_team_edit(request, key):
    return change_entity(request, key, forms.Team)

def app_admin_dashboard_stasis(request):
    _users = users.User.all().filter("is_active", False).order("name").fetch(models.ALL)
    teams = users.Team.all().filter("is_active", False).order("name").fetch(models.ALL)
    for team in teams:
        team.users = utils.get_all_users(team)    
    
    return render_to_response(request,
                              'teammail/app_admin_dashboard.html',
                              data={
        'title': 'Stasisboard',
        'teams': teams,
        'users': _users,
    })
