from django.contrib import admin as django_admin
from teammail import models, admin
from teammail.utils import get_team



class ManagementSite(django_admin.AdminSite):
    app_index_template="teammail/manage/app_index.html"
    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return bool(get_team(request))

site = ManagementSite(name='management')



class InTeam(django_admin.ModelAdmin):
    change_list_template = "teammail/manage/change_list.html"
    delete_confirmation_template = "teammail/manage/delete_selected_confirmation.html"
    object_history_template = "teammail/manage/object_history.html"
    change_form_template = "teammail/manage/change_form.html"
    exclude = ('changed_by', 'last_changed', 'added_by', 'added_date', 'team')
    
    def save_form(self, request, form, change):
        return form.save(commit=False, initialize={ 'team': get_team(request)})

    def _in_team(self, obj, request):
        if not obj:
            return True
        team = get_team(request)
        return obj.team.key().id() == team.key().id()

    def has_add_permission(self, request):
        return bool(get_team(request))

    def has_change_permission(self, request, obj=None):
        return self._in_team(obj, request)

    def has_delete_permission(self, request, obj=None):
        return self._in_team(obj, request)

    def queryset(self, request):
        """
        Returns a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.model.all().filter('team', get_team(request))
        if self.ordering:
            for order in self.ordering:
                qs.order(order)
        return qs



class Division(InTeam, admin.Report):
    pass

#site.register(models.Division, Division)



class Contact(InTeam, admin.Contact):
    pass

site.register(models.Contact, Contact)



class Report(InTeam, admin.Report):
    pass

site.register(models.Report, Report)



class Template(InTeam, admin.Template):
    pass

site.register(models.Template, Template)
