# coding: utf-8
from django.db import models
from django.utils.importlib import import_module


def create_model(name, module='model_creator.models', fields={}, meta={}):
    model_module = import_module(module)

    if hasattr(model_module, name):
        raise NameError('{module}.{model} already exists'.format(
            module=module,
            model=name
        ))

    properties = {}
    properties.update(fields)
    properties['__module__'] = module
    properties['Meta'] = type(
        'Meta',
        (object,),
        meta
    )

    model = type(
        name,
        (models.Model,),
        properties
    )

    setattr(model_module, name, model)

    return model
