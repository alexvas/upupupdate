import re, copy, datetime, logging
from google.appengine.api import mail as ae_mail
from ragendja.template import render_to_string
from teammail import models, dating, utils

#FROM_ADDRESS = 'A.A.Vasiljev@gmail.com'
FROM_ADDRESS = 'Up up update! <update@upupupdate.com>'
REPLY_ADDRESS = 'incoming@smtp2web.com'

MIME_IMAGES = ('image/x-ms-bmp', 'image/gif', 'image/jpeg', 'image/png', 'image/tiff')
MAX_SIZE = 200

QUOTATION = ("^^^ Reply above this line to post a reply ^^^")
QUOTATION_HTML = ('<tr class="upupupdate_quote"><td>' + QUOTATION + '<hr/></td></tr>')

HALF_A_DAY = datetime.timedelta(hours=12)
FIVE_MINUTES = datetime.timedelta(minutes=5)

def _get_scaled_name(name):
    if name.endswith('.jpg'):
        return name
    name = re.sub('\.\w{3-4}$', '.jpg', name)
    if name.endswith('.jpg'):
        return name
    return name + '.jpg'


def _send_team_mail(team, to, subject, html, text, cc=None, reply_to=None):
    if reply_to is None:
        reply_to = "%s <%s>" % (team.name, REPLY_ADDRESS)

    

    if reply_to:        
        m = ae_mail.EmailMessage(
                            sender=FROM_ADDRESS,
                            to=to,
                            subject=subject,
                            body=text,
                            reply_to=reply_to,
                            html=html,
                            )
    else:
        m = ae_mail.EmailMessage(
                            sender=FROM_ADDRESS,
                            to=to,
                            subject=subject,
                            body=text,
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


def send_team_common_mail(subject, team, html, text, reply_to=None):
    emails = map(lambda x: x.email, utils.get_users(team))
    emails = filter(lambda x: x, emails)
    if not emails:
        return
    to = ', '.join(emails)
    if not to:
        return
    _send_team_mail(team, to, subject, html, text, reply_to=reply_to)


def _get_report_day():
    now = dating.getLocalTime()
    #logging.error("Now is %s", now.strftime("%A, %m/%d/%Y at %H:%M %Z"))
    # amendment for possible job start delay
    recently = now - FIVE_MINUTES
    start_of_report_day = recently.replace(hour=0, minute=0, second=0, microsecond=0)
    #logging.error("start_of_report_day is %s", start_of_report_day.strftime("%A, %m/%d/%Y at %H:%M %Z"))
    return start_of_report_day


def invitation(request, team):
    html_data = {
                 'team': team,
                 'quotation': QUOTATION_HTML,
                 'homepage':request.build_absolute_uri("/"),
                 }
    text_data = copy.copy(html_data)
    text_data['quotation'] = QUOTATION

    html = render_to_string(request, 'base_invitation_mail.html', data=html_data)
    text = render_to_string(request, 'base_invitation_mail.txt', data=text_data)    
    
    send_team_common_mail(
                            '%s - update request? (%s)' % (team.name, _get_report_day().strftime("%A, %m/%d/%Y")),
                            team,
                            html,
                            text
                            )


def digest(request, team):
    start_of_report_day = _get_report_day()
    
    users = utils.get_users(team)
    absents = []
    reporters = []
    
    for user in users:
        reports = user.report_set.filter('added_date >', start_of_report_day).filter('team', team).fetch(models.ALL)
        if reports:
            report = reports[-1]
            user.message = report.body
            user.local_time = dating.getLocalTime(report.added_date)
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
    send_team_common_mail('%s - daily digest (%s)' % (team.name, start_of_report_day.strftime("%A, %m/%d/%Y")), 
                          team, 
                          html, 
                          text,
                          reply_to=False
                          )
