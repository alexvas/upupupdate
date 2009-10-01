# -*- coding: utf-8 -*-
from django import template
from teammail import models

register = template.Library()

@register.inclusion_tag('teammail/user_report_list.html')
def user_reports(user):
    return {'reports': models.Report.all().filter('user', user).order('-added_date').fetch(20),}
