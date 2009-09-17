# -*- coding: utf-8 -*-
#import logging
import email, re
from HTMLParser import HTMLParser

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required

from ragendja.template import render_to_response
from ragendja.dbutils import get_object_or_404

from teammail import models, mail


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


    def _add_start_tag(self, tag, attrs, slash = False):
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
    
    plain = ''
    html = ''
    fr = ''
    to = ''
    for p in message.walk():
        if ('text/plain' == p.get_content_type()):
            plain = p.get_payload(decode=True)
        elif ('text/html' == p.get_content_type()):
            html = p.get_payload(decode=True)
        f = p.get('from')
        t = p.get('to')
        if not fr: fr = f
        if not to: to = t
    
    body = html or plain
    
    if not (body and fr and to):
        raise Exception("dummy message received: %s" % message)
    
    if '<' in fr and '>' in fr:
        fr = re.sub(r'^[^<]*<([^>]+)>.*$', r'\1', fr)
    contacts = models.Contact.all().filter('email', fr).fetch(models.ALL)
    
    if not contacts:
        raise Exception("no contact for incoming mail from '%s'" % fr)
    
    contact = ''
    if 1 == len(contacts):
        contact = contacts[0]
    else:
        for c in contacts:
            team_name = contact.team.name
            if team_name in to:
                contact = c
                break

    if not contact:
        raise Exception("unknown contact choice (%s) for incoming mail from '%s'" % (', '.join(contacts), fr))

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


@login_required
def fork(request):
    if request.user.is_superuser:
        return HttpResponseRedirect("/admin/");
    else:
        return HttpResponseRedirect("/manage/teammail/");
    
