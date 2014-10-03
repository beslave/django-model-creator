# coding: utf-8
from django.apps import apps
from django.db import models
from django.test import TestCase

from model_creator import models as model_creator_models
from model_creator.logic import create_model


__all__ = ('ModelCreationLogicTestCase',)


class ModelCreationLogicTestCase(TestCase):

    TEST_MODEL_APP = 'model_creator'
    TEST_MODEL_NAME = 'TestModel'

    def setUp(self):
        try:
            del apps.all_models['model_creator'][self.TEST_MODEL_NAME.lower()]
        except:
            pass

        self.dynamic_model_class = model_creator_models.DynamicModel
        self.model_module = model_creator_models

    def test_created_model_is_dynamic_model(self):
        model = create_model(self.model_module, self.TEST_MODEL_NAME)
        self.assertTrue(
            issubclass(model, self.dynamic_model_class),
            'Created model must be a subclass of '
            'model_creator.models.DynamicModel'
        )

    def test_created_model_is_added_to_specific_module(self):
        model = create_model(self.model_module, self.TEST_MODEL_NAME)
        self.assertTrue(
            hasattr(self.model_module, self.TEST_MODEL_NAME),
            'Created model has not added to specific module'
        )
        self.assertEqual(
            getattr(self.model_module, self.TEST_MODEL_NAME),
            model,
            '{model_module}{model_name} is not added module ({model})'.format(
                model_module=self.model_module,
                model_name=self.TEST_MODEL_NAME,
                model=model
            )
        )

    def test_created_model_has_right_fields(self):
        fields = {
            'field1': models.CharField(),
            'field2': models.TextField(),
            'field3': models.IntegerField(),
            'field4': models.BooleanField()
        }
        constants = {
            'CLASS_VAR1': 1,
            'CLASS_VAR2': 2
        }
        attrs = {}
        attrs.update(fields)
        attrs.update(constants)

        model = create_model(
            self.model_module, self.TEST_MODEL_NAME,
            fields=attrs
        )

        for constant_name, constant_value in constants.items():
            self.assertEqual(
                getattr(model, constant_name), constant_value,
                'Created model has incorrect value '
                'for attribute with name "{}"'.format(
                    constant_name
                )
            )

        for field_name, field in fields.items():
            self.assertEqual(
                model._meta.get_field(field_name), field,
                'Fields are not the same'
            )

    def test_created_model_has_right_meta(self):
        meta = {
            'verbose_name': 'Test verbose name',
            'app_label': 'test_app_label',
        }
        model = create_model(
            self.model_module, self.TEST_MODEL_NAME,
            meta=meta
        )
        self.assertEqual(
            model._meta.original_attrs, meta,
            'Meta properties is not equal to specified'
        )
