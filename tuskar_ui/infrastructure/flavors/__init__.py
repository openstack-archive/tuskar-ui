# -*- coding: utf8 -*-

from django.conf import settings


def is_flavor_matching():
    deployment_mode = getattr(settings, 'DEPLOYMENT_MODE', 'scale')
    return deployment_mode.lower() == 'scale'
