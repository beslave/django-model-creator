# coding: utf-8
from django.utils.importlib import import_module

from . import errors
from .models import DynamicModel


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


def get_model(name, module='model_creator.models', fields={}, meta={}):
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
            get_app_label(model_module_name=model_module, model_meta=meta),
            name
        )

    return create_model(model_module, name, fields=fields, meta=meta)
