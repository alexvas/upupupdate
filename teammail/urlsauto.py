# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include
from teammail import manage

rootpatterns = patterns('teammail.views',
    (r'^$', 'main'),
    (r'^cron/mailing$', 'mailing'),
    (r'^incoming$', 'incoming'),
    (r'^wizz_admin$', 'create_admin_user'),
    (r'^smtp2web_d2577e1b08ca67b4.html$', 'empty'),
    (r'^fork/', 'fork'),
    (r'^manage/', include(manage.site.urls)),
)
