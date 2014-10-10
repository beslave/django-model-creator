# coding: utf-8
from imp import reload

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.core.management import call_command
from django.core.urlresolvers import get_resolver
from django.db.utils import OperationalError
from django.utils.importlib import import_module

from . import errors
from .models import DynamicModel, ModelTemplate


def create_model(module, name, fields={}, meta={}):
    properties = {}
    properties.update(fields)
    properties['__module__'] = module.__name__
    properties['Meta'] = type(
        'Meta',
        (object,),
        meta
    )

    model = type(
        name,
        (DynamicModel,),
        properties
    )

    setattr(module, name, model)

    return model


def get_app_label(model_module_name='', model_meta={}):
    """
    Return app_label by model module name or it's meta properties
    """
    if model_meta and model_meta.get('app_label'):
        return model_meta['app_label']

    if model_module_name:
        path = model_module_name.split('.')

        if len(path) < 2:
            raise ValueError(
                'Please provide correct model_module_name. '
                'For example: app.models'
            )

        return model_module_name.split('.')[-2]

    raise ValueError(
        'You must specifie model_module_name or/and meta!'
    )


def clear_model_cache(app_name, model_name):
    app_name = app_name.lower()
    model_name = model_name.lower()

    model = apps.all_models.get(app_name, {}).get(model_name)

    if not model:
        return

    # Try unregister model from admin if it is already registered
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

    # Delete model from django apps registry
    del apps.all_models[app_name][model_name]


def delete_model(app_label, model_name, migrate=False):
    clear_model_cache(
        app_label,
        model_name
    )

    if migrate:
        update_migrations(app_label)


def update_migrations(app_label):
    call_command('makemigrations', app_label, noinput=True)
    call_command('migrate', app_label, noinput=True)

def update_urls():
    reload(import_module(settings.ROOT_URLCONF))

    # Clear resolver cache
    resolver = get_resolver(settings.ROOT_URLCONF)
    resolver._reverse_dict = {}
    resolver._namespace_dict = {}
    resolver._app_dict = {}
    resolver._populated = False


def register_model(name, module, fields={}, meta={}, migrate=False):
    model_module = import_module(module)
    app_label = get_app_label(
        model_module_name=model_module.__name__,
        model_meta=meta
    )

    if hasattr(model_module, name):
        if not issubclass(getattr(model_module, name), DynamicModel):
            raise errors.NameAlreadyExists(
                '{module}.{model} already exists'.format(
                    module=module,
                    model=name
                )
            )
        delete_model(app_label, name)

    model = create_model(model_module, name, fields=fields, meta=meta)

    if migrate:
        update_migrations(app_label)

    admin.site.register(model)
    update_urls()

    return model


def register_model_from_template(model_template, migrate=False):
    register_model(
        model_template.name,
        '{app}.models'.format(app=model_template.app),
        fields=model_template.get_prepared_fields(),
        meta=model_template.get_model_meta(),
        migrate=migrate
    )


def register_models_from_templates():
    try:
        for model_template in ModelTemplate.objects.all():
            register_model_from_template(model_template)
    except OperationalError:
        # Maybe db table for ModelTemplate is not create yet
        pass
