# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from teammail import manage, views as v

rootpatterns = patterns('',
    url(r'^$', v.main),
    url(r'^cron/invitation$', v.invitation),
    url(r'^cron/digest$', v.digest),
    url(r'^incoming$', v.incoming),
#    url(r'^wizz_admin$', v.create_admin_user),
    url(r'^smtp2web_d2577e1b08ca67b4.html$', v.empty),
    url(r'^fork/', v.fork),
    url(r'^manage/', include(manage.site.urls)),
    url(r'^dashboard/$', v.app_admin_dashboard, name='dashboard'),
    url(r'^dashboard/user/(?P<key>\w+)/$', v.app_admin_dashboard_user_edit),
    url(r'^dashboard/team/(?P<key>\w+)/$', v.app_admin_dashboard_team_edit),
    url(r'^dashboard/stasis/$', v.app_admin_dashboard_stasis),
)
