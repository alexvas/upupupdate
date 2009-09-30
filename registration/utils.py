
from django.contrib.auth.forms import PasswordResetForm

def password_reset(request, user, creation=False):
    form = PasswordResetForm()
    form.users_cache = [user]
    if creation:
        email_template_name='registration/create_user_password_reset_email.html'
    else:
        email_template_name='registration/password_reset_email.html'
    if not user.last_login:
        from datetime import datetime
        user.last_login = datetime.now()
        user.put()

    form.save(domain_override=request.get_host(), email_template_name=email_template_name)
