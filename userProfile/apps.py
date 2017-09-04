from __future__ import unicode_literals

from django.apps import AppConfig

class userProfileConfig(AppConfig):
    name = 'userProfile'

    def ready(self):
        from . import signals