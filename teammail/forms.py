# -*- coding: utf-8 -*-
from django import forms
from teammail import models

class UserVisible(forms.ModelForm):
    class Meta:
        exclude = ('changed_by', 'last_changed', 'added_by', 'added_date')

class Team(forms.ModelForm):    
    class Meta(UserVisible.Meta):
        model = models.Team

class Division(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Division

class Contact(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Contact

class Report(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Report

class Template(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Template
