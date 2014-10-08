from collections import OrderedDict

from django.db import models


class ModelFieldTypeRegistry(object):

    __registry__ = OrderedDict()

    def __new__(cls, name, *args, **kwargs):
        if name in cls.__registry__:
            raise NameError('Type {} already registred'.format(name))

        cls.__registry__[name] = super(
            ModelFieldTypeRegistry, cls
        ).__new__(cls)
        cls.__registry__[name].__init__(name, *args, **kwargs)

        return cls.__registry__[name]

    def __init__(self, name, model_field, title=None, **default_attributes):
        self.name = name
        self.model_field = model_field
        self.default_attributes = default_attributes
        self.title = title or self.name

    @classmethod
    def choices(cls):
        return [(x.name, x.title) for x in cls.__registry__.values()]

    @classmethod
    def get(cls, type_name):
        return cls.__registry__[type_name]

    @classmethod
    def get_all(cls):
        return cls.__registry__.values()

    def get_field(self, **field_attrs):
        attrs = {}
        attrs.update(self.default_attributes)
        attrs.update(field_attrs)
        return self.model_field(**attrs)


ModelFieldTypeRegistry('char', models.CharField, max_length=255),
ModelFieldTypeRegistry('int', models.IntegerField),
ModelFieldTypeRegistry('date', models.DateField),
ModelFieldTypeRegistry('datetime', models.DateTimeField),
