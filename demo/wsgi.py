"""
WSGI config for model_creator-demo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")

import django
django.setup()

from model_creator.logic import register_models_from_templates
register_models_from_templates()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
