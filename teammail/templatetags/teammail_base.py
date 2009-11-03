# -*- coding: utf-8 -*-
from django import template
from teammail import models, dating

register = template.Library()

@register.inclusion_tag('teammail/user_report_list.html')
def user_reports(user):
    recent_list = models.Report.all().filter('user', user).order('-added_date').fetch(20)
    for report in recent_list:
        report.local_time = dating.getLocalTime(report.added_date)
    return {'reports': recent_list,}
