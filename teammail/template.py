# -*- coding: utf-8 -*-
from django.template import TemplateDoesNotExist
from teammail import models

def datastore_loader(template_name, template_dirs=None):
    packed = template_name.split('/', 1)
    if len(packed) != 2 or packed[0] != 'datastore':
        raise TemplateDoesNotExist, template_name
                
    template = models.Template.all().filter('name', packed[1]).get()
    if not template:
        raise TemplateDoesNotExist, template_name
    
    return (template.body, template_name)

datastore_loader.is_usable = True

