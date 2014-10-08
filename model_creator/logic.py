# coding: utf-8
from django.apps import apps
from django.contrib import admin
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


def register_model(name, module, fields={}, meta={}):
    model_module = import_module(module)

    if hasattr(model_module, name):
        if not issubclass(getattr(model_module, name), DynamicModel):
            raise errors.NameAlreadyExists(
                '{module}.{model} already exists'.format(
                    module=module,
                    model=name
                )
            )

        clear_model_cache(
            get_app_label(
                model_module_name=model_module.__name__,
                model_meta=meta
            ),
            name
        )

    model = create_model(model_module, name, fields=fields, meta=meta)

    admin.site.register(model)

    return model


def register_models_from_templates():
    for model_template in ModelTemplate.objects.all():
        register_model(
            model_template.name,
            '{app}.models'.format(app=model_template.app),
            fields=model_template.get_prepared_fields(),
            meta=model_template.get_model_meta()
        )
