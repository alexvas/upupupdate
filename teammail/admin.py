from django.contrib import admin

from teammail import models, forms
from teammates import users


    
class Team(admin.ModelAdmin):    
    form = forms.Team

admin.site.register(users.Team, Team)



class Report(admin.ModelAdmin):
    form = forms.Report

admin.site.register(models.Report, Report)



class Template(admin.ModelAdmin):
    form = forms.Template

admin.site.register(models.Template, Template)
