from django.apps import apps
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .field_types_registry import ModelFieldTypeRegistry as types_registry


def get_app_choices():
    return [
        (app_config.name, app_config.verbose_name)
        for app_config in apps.get_app_configs()
    ]


class DynamicModel(models.Model):
    """
    Base class of all dynamic-created models
    """

    class Meta:
        abstract = True


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
        return (self.verbose_name or self.name).capitalize()

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
