import datetime, re
from google.appengine.api import mail as ae_mail
from google.appengine.api import images, users
from django.utils.html import escape
from ragendja.template import render_to_string
from teammail import models

REPLY_ADDRESS = 'ArtSmart News <no-reply@artsmartinstitute.org>'

MIME_IMAGES = ('image/x-ms-bmp', 'image/gif', 'image/jpeg', 'image/png', 'image/tiff')
MAX_SIZE=200

def _get_scaled_name(name):
    if name.endswith('.jpg'):
        return name
    name = re.sub('\.\w{3-4}$', '.jpg', name)
    if name.endswith('.jpg'):
        return name
    return name + '.jpg'

def mail(request, press_item, to_address, sender=REPLY_ADDRESS):
    files = press_item.file_set.fetch(models.ALL)
    for file in files:
        if not file.mime in MIME_IMAGES or file.scaled:
            continue
        file.scaled_name = _get_scaled_name(file.name)
        image = images.Image(file.file)
        image.resize(width=MAX_SIZE, height=MAX_SIZE)
        file.scaled = image.execute_transforms(output_encoding=images.JPEG)
        scaled = images.Image(file.scaled)
        file.scaled_width = scaled.width
        file.scaled_height = scaled.height        
        file.put()

    image_files = []    
    others = []    
    for file in files:
        file.link = request.build_absolute_uri(file.get_absolute_url())
        if file.scaled:
            file.src = request.build_absolute_uri(file.get_thumbnail_url())
            image_files.append(file)
        else:
            others.append(file)

    message = EmailWithEmbeddedImages(
                                      html_template='mrelease/press_item_html_mail.html',
                                      text_template='mrelease/press_item_text_mail.txt',
                                      data=dict(
                                                item=press_item, 
                                                images=image_files, 
                                                others=others,
                                                homepage=request.build_absolute_uri("/"),
                                                body = unicode(escape(press_item.body)),
                                                ),
                                      )
    message.sender = sender
    message.to = to_address
    message.subject = press_item.title
    message.do_send(request)
 
    press_item.last_sent = datetime.datetime.now();
    press_item.put();

    

from email.MIMEImage import MIMEImage

class EmailWithEmbeddedImages(ae_mail.EmailMessage):
    """Derived interface to email API service.
     allows to embed images into html body
    """

    _API_CALL = 'Send'
    PROPERTIES = ae_mail.EmailMessage.PROPERTIES
    PROPERTIES.update(('data', 'html_template', 'text_template'))
  
#    def to_mime_message(self):
#        root = super(EmailWithEmbeddedImages, this).to_mime_message()
#        for img in self.data.get('images', ()):
#            image = MIMEImage(img.file)
#            image.add_header('Content-ID', '<%s>' % img.cid)
#            root.attach(image)

    def __init__(self, **kw):
        if 'data' in kw:
            self.data = kw.pop('data')
        else:
            self.data = {}
        if 'html_template' in kw:
            self.html_template = kw.pop('html_template')
        else:
            self.html_template = ''
        if 'text_template' in kw:
            self.text_template = kw.pop('text_template')
        else:
            self.text_template = ''
        super(EmailWithEmbeddedImages, self).__init__(**kw)
        i = 0
        for img in self.data.get('images', ()):
            img.cid = "image%s" % i
            i = i + 1
            
    def do_send(self, request):
        self.html = render_to_string(
            request,
            self.html_template,
            data=self.data,
        )
        self.body = render_to_string(
            request,
            self.text_template,
            data=self.data,
        )
        self.send()


