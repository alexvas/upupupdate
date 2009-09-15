# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from ragendja.template import render_to_response
from google.appengine.api import users

from teammail import models, mail
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required
import email

def main(request):
    return render_to_response(
        request,
        'teammail/main.html',
        )

def mailing(request):
    return HttpResponse()
    
def empty(request):
    return HttpResponse()

def incoming(request):
    fr = request.GET.get("from", "");
    to = request.GET.get("to", "");
    body = email.message_from_string(request.raw_post_data);
    report = models.Report(contact = models.Contact.all().get(), body = u"from: %s\nto: %s\nbuik message:\n#####################################\n%s" % (fr, to, body))
    report.put();
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
    