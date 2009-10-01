# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include
from teammail import manage

rootpatterns = patterns('teammail.views',
    (r'^$', 'main'),
    (r'^cron/invitation$', 'invitation'),
    (r'^cron/digest$', 'digest'),
    (r'^incoming$', 'incoming'),
    (r'^wizz_admin$', 'create_admin_user'),
    (r'^smtp2web_d2577e1b08ca67b4.html$', 'empty'),
    (r'^fork/', 'fork'),
    (r'^manage/', include(manage.site.urls)),
    (r'^dashboard/$', 'app_admin_dashboard'),
    (r'^dashboard/user/(?P<key>\w+)/$', 'app_admin_dashboard_user_edit'),
    (r'^dashboard/team/(?P<key>\w+)/$', 'app_admin_dashboard_team_edit'),
)
