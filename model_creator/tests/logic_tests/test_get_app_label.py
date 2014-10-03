# coding: utf-8
from django.test import TestCase

from model_creator.logic import get_app_label


class GetAppLabelTestCase(TestCase):

    def test_get_app_label_by_module_name(self):
        self.assertEqual(
            get_app_label(model_module_name='app.models'),
            'app'
        )

        self.assertEqual(
            get_app_label(model_module_name='app.contrib.auth.models'),
            'auth',
            'app_label from "app.contrib.auth.models" is "auth"'
        )
