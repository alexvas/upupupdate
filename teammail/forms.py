# -*- coding: utf-8 -*-
from django import forms
from teammail import models, utils
from teammates import users

class UniqueField(forms.CharField):
    def clean(self, value):
        value = value.strip()
        self.check_uniqueness(value)
        return super(UniqueField, self).clean(value)

    def check_uniqueness(self, value):
        pass


class UniqueUserEmailField(UniqueField):
    default_error_messages = {
        'already_registered_for': u"The '%s' is already registered for the user '%s'.",
        'already_registered': u"The '%s' is already registered.",
        'already_registered_for_inactive': u"The '%s' is already registered for the inactive user '%s'.",
        'already_registered_inactive': u"The '%s' is already registered for the inactive user.",
    }

    def __init__(self, *args, **kw):
        kw['help_text'] = u'unique email address'
        kw['min_length'] = 9
        kw['max_length'] = 30
        kw['error_messages'] = {'required': u'Please provide an email.'}
        
        super(UniqueUserEmailField, self).__init__(*args, **kw)

    def check_uniqueness(self, value):
        same_user = users.User.all().filter('email', value).get()
        if same_user:
            if not same_user.is_active:
                if same_user.name:
                    raise forms.ValidationError(self.error_messages['already_registered_for_inactive'] % (value, same_user.name))
                else:
                    raise forms.ValidationError(self.error_messages['already_registered_inactive'] % value)            
            
            if same_user.name:
                raise forms.ValidationError(self.error_messages['already_registered_for'] % (value, same_user.name))
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
        same_team = users.Team.all().filter("name", value).get()
        if same_team:
                raise forms.ValidationError(self.error_messages['already_exists'] % value)


class UserTeamsField(forms.MultipleChoiceField):
    def __init__(self, user=None, *args, **kw):
        kw['required'] = False
        kw['choices'] = utils.get_team_choices()
        if user:
            kw['initial'] = user.teams
        
        super(UserTeamsField, self).__init__(*args, **kw)

    def widget_attrs(self, widget):
        return {'size': 5}


class UserVisible(forms.ModelForm):
    class Meta:
        exclude = ('changed_by', 'last_changed', 'added_by', 'added_date')


class Team(forms.ModelForm):    
    class Meta(UserVisible.Meta):
        model = users.Team


class Report(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Report


class Template(forms.ModelForm):
    class Meta(UserVisible.Meta):
        model = models.Template



class TeamAdminAddUser(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueUserEmailField()


class TeamAdminUserListEntry(forms.Form):
    in_team = forms.BooleanField(required=False)


class AppAdminAddUser(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueUserEmailField()

    def __init__(self, *args, **kw):
        kw['prefix'] = 'app_admin_add_user'
        
        super(AppAdminAddUser, self).__init__(*args, **kw)
        self.fields['teams'] = UserTeamsField()



class AppAdminAddTeam(forms.Form):
    name = UniqueTeamNameField()

    def __init__(self, *args, **kw):
        kw['prefix'] = 'app_admin_add_team'
        
        super(AppAdminAddTeam, self).__init__(*args, **kw)



class AppAdminUserListEntry(forms.Form):
    flag = forms.BooleanField(required=False)


class AppAdminChangeUser(forms.Form):
    name = forms.CharField(required=False)
    email = UniqueUserEmailField()
    inactivate = forms.BooleanField(required=False)


class AppAdminTeamListEntry(forms.Form):
    flag = forms.BooleanField(required=False)


class AppAdminChangeTeam(forms.Form):
    name = UniqueTeamNameField()
    inactivate = forms.BooleanField(required=False)


