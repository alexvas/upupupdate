import re, copy, datetime
from google.appengine.api import mail as ae_mail
from ragendja.template import render_to_string
from teammail import models, dating, utils

FROM_ADDRESS = 'Up up update! <update@upupupdate.com>'
REPLY_ADDRESS = 'incoming@smtp2web.com'

MIME_IMAGES = ('image/x-ms-bmp', 'image/gif', 'image/jpeg', 'image/png', 'image/tiff')
MAX_SIZE = 200

QUOTATION = ("^^^ Reply above this line to post a reply ^^^")
QUOTATION_HTML = ('<tr class="upupupdate_quote"><td>' + QUOTATION + '<hr/></td></tr>')

HALF_A_DAY = datetime.timedelta(hours=12)

def _get_scaled_name(name):
    if name.endswith('.jpg'):
        return name
    name = re.sub('\.\w{3-4}$', '.jpg', name)
    if name.endswith('.jpg'):
        return name
    return name + '.jpg'


def _send_team_mail(team, to, subject, html, text, cc=None):
    reply_to = "%s <%s>" % (team.name, REPLY_ADDRESS)
    m = ae_mail.EmailMessage(
                            sender=FROM_ADDRESS,
                            to=to,
                            subject=subject,
                            body=text,
                            reply_to=reply_to,
                            html=html,
                            )
    if cc:
        m.cc = cc
    m.send()


def send_team_personal_mail(request, subject, team, html_template, text_template, html_data, text_data):
    for user in utils.get_users(team):
        html_data['user'] = user
        text_data['user'] = user
        html = render_to_string(request, html_template, html_data)
        text = render_to_string(request, text_template, text_data)
        _send_team_mail(team, user.email, subject, html, text)


def send_team_common_mail(subject, team, html, text):
    emails = map(lambda x: x.email, utils.get_users(team))
    emails = filter(lambda x: x, emails)
    if not emails:
        return
    to = emails.pop()
    if not to:
        return
    _send_team_mail(team, to, subject, html, text, cc=', '.join(emails))


def invitation(request, team):
    html_data = {
                 'team': team,
                 'quotation': QUOTATION_HTML,
                 'homepage':request.build_absolute_uri("/"),
                 }
    text_data = copy.copy(html_data)
    text_data['quotation'] = QUOTATION
    send_team_personal_mail(
                            request,
                            'Update email',
                            team,
                            'base_invitation_mail.html',
                            'base_invitation_mail.txt',
                            html_data,
                            text_data
                            )


def digest(request, team):
    now = dating.getLocalTime()
    some_noon = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if some_noon + HALF_A_DAY > now:
        start_of_report_day = some_noon - 2 * HALF_A_DAY
    else:
        start_of_report_day = some_noon
    
    users = utils.get_users(team)
    absents = []
    reporters = []
    
    for user in users:
        reports = user.report_set.filter('added_date >', start_of_report_day).filter('team', team).fetch(models.ALL)
        if reports:
            user.message = reports[-1].body
            reporters.append(user)
        else:
            absents.append(user)
    
    data = {
                 'homepage':request.build_absolute_uri("/"),
                 'absents':absents,
                 'reporters':reporters,
                 }
    html = render_to_string(request, 'base_summary_mail.html', data=data)
    text = render_to_string(request, 'base_summary_mail.txt', data=data)
    send_team_common_mail('Team email', team, html, text)
