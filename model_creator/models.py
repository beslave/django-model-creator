from django.apps import apps
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from . import settings as model_creator_settings
from .field_types_registry import ModelFieldTypeRegistry as types_registry


def get_app_choices():
    return [
        (app_config.name, app_config.verbose_name)
        for app_config in apps.get_app_configs()
        if app_config.name in model_creator_settings.DYNAMIC_APPS
    ]


class ObjectField(object):
    """
    Field of model object with it's value and template
    """

    def __init__(self, value, template):
        self.value = value
        self.template = template


class DynamicModel(models.Model):
    """
    Base class of all dynamic-created models
    """

    class Meta:
        abstract = True

    @classmethod
    def all_models(cls):
        models_for_apps = {}

        for model in apps.get_models():
            if model._meta.abstract or not issubclass(model, cls):
                continue

            app_label = model._meta.app_label
            models_for_apps.setdefault(app_label, [])
            models_for_apps[app_label].append(model)

        return models_for_apps

    @classmethod
    def get_model(cls, app_label, model_name):
        models = cls.all_models().get(app_label, [])
        models = [
            x for x in models
            if x.__name__.lower() == model_name.lower()
        ]
        return models[0] if models else None

    @classmethod
    def model_meta_options(cls):
        return cls._meta

    @classmethod
    def model_name(cls):
        return cls.__name__

    @classmethod
    def template(cls):
        if '__model_template__' not in vars(cls):
            app = cls._meta.app_label
            name = cls.__name__
            template = ModelTemplate.objects.get(app=app, name=name)
            cls.__model_template__ = template
        return cls.__model_template__

    @classmethod
    def template_fields(cls):
        if '__model_template_fields__' not in vars(cls):
            tpl = cls.template()
            fields = list(tpl.fields.all())
            cls.__model_template_fields__ = fields
        return cls.__model_template_fields__

    def object_fields(self):
        if '__object_template_fields__' not in vars(self):
            fields = [
                ObjectField(
                    getattr(self, field_template.name),
                    field_template
                ) for field_template in self.template_fields()
            ]
            self.__object_template_fields__ = fields
        return self.__object_template_fields__


class ModelTemplate(models.Model):
    """
    Template for dynamic models
    """

    app = models.CharField(
        max_length=128,
        null=False,
        verbose_name=_('application where model will be created'),
    )

    name = models.CharField(
        max_length=64,
        null=False,
        validators=[
            RegexValidator(
                r'[a-zA-Z0-9]+',
                message=_('Name can contain only latin characters and numbers')
            )
        ],
        verbose_name=_('name for model'),
    )

    verbose_name = models.CharField(
        blank=True,
        max_length=128,
        null=True,
        verbose_name=_('verbose name (title) for model'),
    )

    class Meta:
        unique_together = [
            ('app', 'name'),
        ]
        verbose_name = _('template for dynamic model')
        verbose_name_plural = _('templates for dynamic models')

    def __str__(self):
        return 'Model template for "{}"'.format(
            (self.verbose_name or self.name).capitalize()
        )

    def get_model_meta(self):
        return {
            'verbose_name': self.verbose_name or self.name
        }

    def get_prepared_fields(self):
        fields = {}
        for field in self.fields.all():
            model_field = types_registry.get(field.field_type).get_field(
                verbose_name=field.verbose_name or field.name
            )
            fields[field.name] = model_field
        return fields


class ModelTemplateField(models.Model):
    """
    Field of dynamic model
    """

    model_template = models.ForeignKey(
        ModelTemplate,
        blank=False,
        null=False,
        related_name='fields',
        verbose_name=_('model field')
    )

    field_type = models.CharField(
        max_length=16,
        choices=types_registry.choices()
    )

    name = models.CharField(
        blank=False,
        max_length=32,
        null=False,
        validators=[
            RegexValidator(
                r'[0-9a-zA-Z_]+',
                message=_(
                    'Name can contain only latin letters, numbers and "_"'
                )
            )
        ],
        verbose_name=_('name of field'),
    )

    verbose_name = models.CharField(
        blank=True,
        default='',
        max_length=64,
        null=False,
        verbose_name=_('verbose name of field')
    )

    class Meta:
        unique_together = [
            ('name', 'model_template'),
        ]
        verbose_name = _('Field for model template')
        verbose_name_plural = _('Fields for model templates')


def get_model_template(sender, instance):
    if sender == ModelTemplate:
        return instance
    return instance.model_template


@receiver(post_save, sender=ModelTemplate)
@receiver(post_save, sender=ModelTemplateField)
@receiver(pre_delete, sender=ModelTemplateField)
def on_template_update(sender, **kwargs):
    from .logic import register_model_from_template, update_migrations

    model_template = get_model_template(sender, kwargs.pop('instance'))
    register_model_from_template(model_template)
    update_migrations(model_template.app)


@receiver(pre_delete, sender=ModelTemplate)
def on_template_delete(sender, **kwargs):
    from .logic import delete_model, update_migrations

    model_template = kwargs.pop('instance')
    delete_model(model_template.app, model_template.model_name, migrate=True)
    update_migrations(model_template.app)
