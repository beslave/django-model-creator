from collections import OrderedDict

from json import loads as json_load
from yaml import load as yaml_load
from xml.dom.minidom import parseString as xml_load

from django.db import transaction

from .models import ModelTemplate, ModelTemplateField


class Importer(object):
    """
    Create new model templates and their fields from importing data
    """

    SUPPORT_TYPE = None  # Please provide supported types in subclasses

    def __init__(self, data, app):
        self.app = app
        self.data = self._parse(data)

    @staticmethod
    def _parse(data):
        """
        Parse input data to format:

        {
            "FirstExampleModel": {
                "verbose_name": "Model One",
                "fields": [
                    {"name": "field1", "verbose_name": "Field 1", "type": "int"},
                    {"name": "field2", "verbose_name": "Field 2", "type": "char"},
                    {"name": "field3", "verbose_name": "Field 3", "type": "date"}
                ]
            },
            "SecondExampleModel": {
                "verbose_name": "Model Two",
                "fields": [
                    {"name": "field1", "verbose_name": "Field 1", "type": "int"},
                    {"name": "field2", "verbose_name": "Field 2", "type": "char"},
                    {"name": "field3", "verbose_name": "Field 3", "type": "date"}
                ]
            }
        }
        """
        raise NotImplemented

    @classmethod
    def get_importers(cls):
        """
        Return dict with supported data types as keys
        and appropriate importers
        """
        importers = [
            (importer.SUPPORT_TYPE, importer)
            for importer in cls.__subclasses__()
            if importer.SUPPORT_TYPE
        ]
        importers.sort()
        return OrderedDict(importers)

    @classmethod
    def get_importer_by_type(cls, data_type):
        return cls.get_importers()[data_type]

    @transaction.atomic
    def save(self):
        for model_name, model_data in self.data.items():
            model_template, is_created = ModelTemplate.objects.get_or_create(
                app=self.app,
                name=model_name,
                defaults={
                    'verbose_name': model_data['verbose_name']
                }
            )

            if not is_created:
                model_template.verbose_name = model_data['verbose_name']
                model_template.save()

            actual_field_pks = []

            for field_data in model_data['fields']:
                field, is_new_field = ModelTemplateField.objects.get_or_create(
                    model_template=model_template,
                    name=field_data['name'],
                    defaults={
                        'field_type': field_data['type'],
                        'verbose_name': field_data['verbose_name']
                    }
                )
                if not is_new_field:
                    field.field_type = field_data['type']
                    field.verbose_name = field_data['verbose_name']
                    field.save()

                actual_field_pks.append(field.pk)

            # Delete out of date fields
            model_template.fields.exclude(pk__in=actual_field_pks).delete()


class YAMLImporter(Importer):
    """
    Input data must be in same format as:

    FirstExampleModel:
        title: Model One
        fields:
            - {id: field1, title: Field 1, type: int}
            - {id: field2, title: Field 2, type: char}
            - {id: field3, title: Field 3, type: data}

    SecondExampleModel:
        title: Model Two
        fields:
            - {id: field1, title: Field 1, type: int}
            - {id: field2, title: Field 2, type: char}
            - {id: field3, title: Field 3, type: data}
    """

    SUPPORT_TYPE = 'yaml'

    @staticmethod
    def _parse(data):
        source_data = yaml_load(data)
        data = {}
        for model_name, model_description in source_data.items():
            fields = []
            for field_data in model_description['fields']:
                fields.append({
                    'name': field_data['id'],
                    'type': field_data['type'],
                    'verbose_name': field_data['title']
                })
            data[model_name] = {
                'verbose_name': model_description['title'],
                'fields': fields
            }
        return data


class JSONImporter(Importer):
    """
    Input data must be in same format as:

    {
        "FirstExampleModel": {
            "verbose_name": "Model One",
            "fields": [
                {"name": "field1", "verbose_name": "Field 1", "type": "int"},
                {"name": "field2", "verbose_name": "Field 2", "type": "char"},
                {"name": "field3", "verbose_name": "Field 3", "type": "date"}
            ]
        },
        "SecondExampleModel": {
            "verbose_name": "Model Two",
            "fields": [
                {"name": "field1", "verbose_name": "Field 1", "type": "int"},
                {"name": "field2", "verbose_name": "Field 2", "type": "char"},
                {"name": "field3", "verbose_name": "Field 3", "type": "date"}
            ]
        }
    }
    """

    SUPPORT_TYPE = 'json'

    @staticmethod
    def _parse(data):
        return json_load(data)


class XMLImporter(Importer):
    """
    Input data must be in same format as:

    <models>
        <FirstExampleModel>
            <verbose_name>Model One</verbose_name>
            <fields>
                <field1>
                    <verbose_name>Field 1</verbose_name>
                    <type>int</type>
                </field1>
                <field2>
                    <verbose_name>Field 2</verbose_name>
                    <type>char</type>
                </field2>
                <field3>
                    <verbose_name>Field 3</verbose_name>
                    <type>date</type>
                </field3>
            </fields>
        </FirstExampleModel>
        <SecondExampleModel>
            <verbose_name>Model Two</verbose_name>
            <fields>
                <field1>
                    <verbose_name>Field 1</verbose_name>
                    <type>int</type>
                </field1>
                <field2>
                    <verbose_name>Field 2</verbose_name>
                    <type>char</type>
                </field2>
                <field3>
                    <verbose_name>Field 3</verbose_name>
                    <type>date</type>
                </field3>
            </fields>
        </SecondExampleModel>
    </models>
    """

    SUPPORT_TYPE = 'xml'

    @staticmethod
    def _parse(data):
        data = ''.join(map(lambda x: x.strip(), data.split('\n')))

        model_nodes = xml_load(data).childNodes[0].childNodes
        data = {}

        get_by_key = lambda node, k: [
            x for x in node.childNodes if x.nodeName == k
        ][0].childNodes[0].nodeValue

        for model_node in model_nodes:
            model_data = {}

            model_data['verbose_name'] = get_by_key(model_node, 'verbose_name')
            model_data['fields'] = []

            fields = model_node.getElementsByTagName('fields')[0].childNodes

            for field_node in fields:
                model_data['fields'].append({
                    'name': field_node.nodeName,
                    'type': get_by_key(field_node, 'type'),
                    'verbose_name': get_by_key(field_node, 'verbose_name')
                })

            data[model_node.nodeName] = model_data

        return data
