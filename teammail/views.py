# -*- coding: utf-8 -*-
#import logging
from HTMLParser import HTMLParser
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required
#from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseForbidden
from ragendja.auth.decorators import staff_only
from ragendja.template import render_to_response
from teammail import models, forms, mail, utils
import email
import re


#from ragendja.dbutils import get_object_or_404


def main(request):
    return render_to_response(
        request,
        'teammail/main.html',
        )


def _get_active_teams():
    return models.Team.all().filter('is_active', True).fetch(models.ALL)


def invitation(request):
    for team in _get_active_teams():
        mail.invitation(request, team)
    return HttpResponse()


def summary(request):
    for team in _get_active_teams():
        mail.summary(request, team)
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


def incoming(request):
    message = email.message_from_string(request.raw_post_data);
    import logging
    
    plain = u''
    html = u''
    fr = u''
    to = u''
    for p in message.walk():
        charset = 'utf-8'
        c = p.get_charset()
        if c:
            charset = c
        logging.debug(u"charset is %s", charset)
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
    contact = models.Contact.all().filter('email', fr).get()
    
    if not contact:
        raise Exception("no contact for incoming mail from '%s'" % fr)
    
    team = None
    for t in contact.teams:
        if t in to:
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

    models.Report(contact=contact, body=body).put()
    return HttpResponse()


def create_admin_user(request):
    user = auth_models.User.get_by_key_name('admin')
    if not user or user.username != 'admin' or not (user.is_active and
            user.is_staff and user.is_superuser and
            user.check_password('admin')):
        user = auth_models.User(key_name='admin', username='admin',
            email='admin@localhost', first_name='Boss', last_name='Admin',
            is_active=True, is_staff=True, is_superuser=True)
        user.set_password('adminno')
        user.put()
    return HttpResponse()

@staff_only
def team_admin_dashboard(request):
    # TODO: embed add form into each contact 
    if request.method == 'POST':
        if 'create_contact' in request.POST:
            formCreate = forms.TeamAdminAddContact(request.POST)
            formAdd = forms.TeamAdminContactListEntry()
            if formCreate.is_valid():
                cleaned_data = formCreate.cleaned_data
                models.Contact(name=cleaned_data['name'], email=cleaned_data['email'])
                return HttpResponseRedirect(request.get_full_path())
        elif 'add_contact' in request.POST:
            formAdd = forms.TeamAdminContactListEntry(request.POST)
            formCreate = forms.TeamAdminAddContact()
            if formAdd.is_valid():
                cleaned_data = formCreate.cleaned_data
                # TODO: add code 
                return HttpResponseRedirect(request.get_full_path())
        else:
            return HttpResponseRedirect(request.get_full_path())
    else:
        formCreate = forms.TeamAdminAddContact()
        formAdd = forms.TeamAdminContactListEntry()

    return render_to_response('team_admin_dashboard', {
        'formAdd': formAdd,
        'formCreate': formCreate,
    })


def _embed_application_admin_contact_list_forms(contacts, request=None):
    for contact in contacts:
        if request:
            contact.form = forms.AppAdminContactListEntry(request.POST, prefix=unicode(contact.key()), auto_id=False) 
        else:
            contact.form = forms.AppAdminContactListEntry(prefix=unicode(contact.key()), auto_id=False)
        contact.form.fields['teams'] = forms.ContactTeamsField(contact=contact)


def _embed_application_admin_team_list_forms(teams, request=None):
    for team in teams:
        if request:
            team.form = forms.AppAdminTeamListEntry(request.POST, prefix=unicode(team.key()), auto_id=False) 
        else:
            team.form = forms.AppAdminTeamListEntry(prefix=unicode(team.key()), auto_id=False) 


def update_team_set(contact, teams):
    was = set(contact.teams)
    _is = set(teams)
    if was != _is:
        contact.teams = _is
        contact.put()


@staff_only
def app_admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    contacts = models.Contact.all().filter("is_active", True).order("name").fetch(models.ALL)
    teams = models.Team.all().filter("is_active", True).order("name").fetch(models.ALL)
    for team in teams:
        team.contacts = utils.get_contacts(team)    

    formAddTeam = None
    formAddContact = None
    
    action = None
    if request.method == 'POST' and 'action' in request.POST:
        action = request.POST['action']
    
    add_contact_to_team = None
    if request.method == 'POST' and 'add_contact_to_team' in request.POST:
        add_contact_to_team = request.POST['add_contact_to_team']
    
    if add_contact_to_team:
        num = add_contact_to_team.split('_')[1]
        num = int(num)
        team = teams[num]
        email = request.POST[add_contact_to_team]
        email = re.sub(r'^[^<]*<([^>]+)>.*$', r'\1', email)
        contact = models.Contact.all().filter("email", email).get()
        if contact:
            contact.teams.append(team.key())
            contact.put()
                    
        return HttpResponseRedirect(request.get_full_path())

    elif 'add_team' == action:
        formAddTeam = forms.AppAdminAddTeam(request.POST)
        
        if formAddTeam.is_valid():
            cleaned_data = formAddTeam.cleaned_data
            models.Team(name=cleaned_data['name']).put()
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
        
    elif 'add_contact' == action:
        formAddContact = forms.AppAdminAddContact(request.POST)
        
        if formAddContact.is_valid():
            cleaned_data = formAddContact.cleaned_data
            
            teams = models.Team.get(cleaned_data['teams'])
            if teams:
                teams = filter(lambda x: x, teams)
                teams = map(lambda x: x.key(), teams)
            contact = models.Contact(name=cleaned_data['name'], email=cleaned_data['email'])
            if teams:
                contact.teams = teams
            contact.put()
            return HttpResponseRedirect(request.get_full_path())
        
    elif 'assign_teams_to_contacts' == action:
        _embed_application_admin_contact_list_forms(contacts, request)
        
        valid = True
        for contact in contacts:
            if not contact.form.is_valid():
                valid = False
                continue
            cleaned_data = contact.form.cleaned_data
            update_team_set(contact, cleaned_data['teams'])
            
        if valid:
            return HttpResponseRedirect(request.get_full_path())
        
    elif 'inactivate_contacts' == action:
        _embed_application_admin_contact_list_forms(contacts, request)

        valid = True
        for contact in contacts:
            if not contact.form.is_valid():
                valid = False
                continue
            
        if valid:
            for contact in contacts:
                cleaned_data = contact.form.cleaned_data
                if cleaned_data['flag'] == u'on':
                    contact.is_active = False
                    contact.put()
            return HttpResponseRedirect(request.get_full_path())
            

    if not formAddTeam:
        formAddTeam = forms.AppAdminAddTeam()

    if not formAddContact:
        formAddContact = forms.AppAdminAddContact()
        
    if teams and not 'form' in dir(teams[0]):
        _embed_application_admin_team_list_forms(teams)
        
    if contacts and not 'form' in dir(contacts[0]):
        _embed_application_admin_contact_list_forms(contacts)

    return render_to_response(request,
                              'teammail/app_admin_dashboard.html',
                              data={
        'formAddTeam': formAddTeam,
        'formAddContact': formAddContact,
        'teams': teams,
        'contacts': contacts,
    })
    
    
@login_required
def fork(request):
    if request.user.is_superuser:
        return HttpResponseRedirect('/dashboard/');
    else:
        return HttpResponseRedirect('/manage/teammail/');
