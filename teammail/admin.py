from django.contrib import admin

from teammail import models, forms

    
class Team(admin.ModelAdmin):    
    form = forms.Team

admin.site.register(models.Team, Team)


class Division(admin.ModelAdmin):
    form = forms.Division

admin.site.register(models.Division, Division)


class Contact(admin.ModelAdmin):
    form = forms.Contact

admin.site.register(models.Contact, Contact)


class Report(admin.ModelAdmin):
    form = forms.Report

admin.site.register(models.Report, Report)


class Template(admin.ModelAdmin):
    form = forms.Template

admin.site.register(models.Template, Template)
