# -*- coding: utf-8 -*-
from django import forms
from teammail import models, utils


class UniqueField(forms.CharField):
    def clean(self, value):
        value = value.strip()
        self.check_uniqueness(value)
        return super(UniqueField, self).clean(value)

    def check_uniqueness(self, value):
        pass


class UniqueContactEmailField(UniqueField):
    default_error_messages = {
        'already_registered_for': u"The '%s' is already registered for the user '%s'.",
        'already_registered': u"The '%s' is already registered.",
    }

    def __init__(self, *args, **kw):
        kw['help_text'] = u'unique email address'
        kw['min_length'] = 9
        kw['max_length'] = 30
        kw['error_messages'] = {'required': u'Please provide an email.'}
        
        super(UniqueContactEmailField, self).__init__(*args, **kw)

    def check_uniqueness(self, value):
        same_contact = models.Contact.all().filter("email", value).get()
        if same_contact:
            if same_contact.name:
                raise forms.ValidationError(self.error_messages['already_registered_for'] % (value, same_contact.name))
            else:
                raise forms.ValidationError(self.error_messages['already_registered'] % value)


class UniqueTeamNameField(UniqueField):
    default_error_messages = {
        'already_exists': u"The team '%s' already exists.",
    }

    def __init__(self, *args, **kw):
        kw['help_text'] = u'unique team name'
        kw['min_length'] = 3
        kw['max_length'] = 50
        kw['error_messages'] = {'required': u'Please provide a team name.'}
        
        super(UniqueTeamNameField, self).__init__(*args, **kw)

    def check_uniqueness(self, value):
        same_contact = models.Team.all().filter("name", value).get()
        if same_contact:
                raise forms.ValidationError(self.error_messages['already_exists'] % value)



class ContactTeamsField(forms.MultipleChoiceField):
    def __init__(self, contact=None, *args, **kw):
        kw['required'] = False
        kw['choices'] = utils.get_team_choices()
        if contact:
            kw['initial'] = contact.teams
        
        super(ContactTeamsField, self).__init__(*args, **kw)

    def widget_attrs(self, widget):
        return {'size': 5}


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



class TeamAdminAddContact(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueContactEmailField()


class TeamAdminContactListEntry(forms.Form):
    in_team = forms.BooleanField(required=False)


class AppAdminAddContact(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueContactEmailField()
    teams = ContactTeamsField()

    def __init__(self, *args, **kw):
        kw['prefix'] = 'app_admin_add_contact'
        
        super(AppAdminAddContact, self).__init__(*args, **kw)



class AppAdminAddTeam(forms.Form):
    name = UniqueTeamNameField()

    def __init__(self, *args, **kw):
        kw['prefix'] = 'app_admin_add_team'
        
        super(AppAdminAddTeam, self).__init__(*args, **kw)



class AppAdminContactListEntry(forms.Form):
    flag = forms.BooleanField(required=False)


class AppAdminChangeContact(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueContactEmailField()
    inactivate = forms.BooleanField(required=False)


class AppAdminTeamListEntry(forms.Form):
    flag = forms.BooleanField(required=False)


class AppAdminChangeTeam(forms.Form):
    name = UniqueTeamNameField()
    inactivate = forms.BooleanField(required=False)


