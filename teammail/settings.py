# -*- coding: utf-8 -*-
from ragendja.settings_post import settings

settings.add_app_media('combined-%(LANGUAGE_DIR)s.css',
    'teammail/general.css',
    'teammail/standard.css',
)

loaders = list(getattr(settings, 'TEMPLATE_LOADERS', None))
loaders.append('teammail.template.datastore_loader')
setattr(settings, 'TEMPLATE_LOADERS', tuple(loaders))
