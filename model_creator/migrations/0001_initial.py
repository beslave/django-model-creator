# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('app', models.CharField(max_length=128, verbose_name='application where model will be created')),
                ('name', models.CharField(max_length=64, validators=[django.core.validators.RegexValidator('[a-zA-Z0-9]+', message='Name can contain only latin characters and numbers')], verbose_name='name for model')),
                ('verbose_name', models.CharField(null=True, max_length=128, blank=True, verbose_name='verbose name (title) for model')),
            ],
            options={
                'verbose_name': 'template for dynamic model',
                'verbose_name_plural': 'templates for dynamic models',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ModelTemplateField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('field_type', models.CharField(max_length=16, choices=[('char', 'char type'), ('int', 'int type'), ('date', 'date type'), ('datetime', 'datetime type')])),
                ('name', models.CharField(max_length=32, validators=[django.core.validators.RegexValidator('[0-9a-zA-Z_]+', message='Name can contain only latin letters, numbers and "_"')], verbose_name='name of field')),
                ('verbose_name', models.CharField(max_length=64, default='', blank=True, verbose_name='verbose name of field')),
                ('model_template', models.ForeignKey(to='model_creator.ModelTemplate', related_name='fields', verbose_name='model field')),
            ],
            options={
                'verbose_name': 'Field for model template',
                'verbose_name_plural': 'Fields for model templates',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='modeltemplatefield',
            unique_together=set([('name', 'model_template')]),
        ),
        migrations.AlterUniqueTogether(
            name='modeltemplate',
            unique_together=set([('app', 'name')]),
        ),
    ]
