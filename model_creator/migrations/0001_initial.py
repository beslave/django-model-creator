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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('app', models.CharField(max_length=128, verbose_name='application where model will be created')),
                ('name', models.CharField(max_length=64, verbose_name='name for model', validators=[django.core.validators.RegexValidator('[a-zA-Z0-9]+', message='Name can contain only latin characters and numbers')])),
                ('verbose_name', models.CharField(max_length=128, verbose_name='verbose name (title) for model', blank=True, null=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('field_type', models.CharField(max_length=16, choices=[('char', 'char'), ('int', 'int'), ('date', 'date'), ('datetime', 'datetime')])),
                ('name', models.CharField(max_length=32, verbose_name='name of field', validators=[django.core.validators.RegexValidator('[0-9a-zA-Z_]+', message='Name can contain only latin letters, numbers and "_"')])),
                ('verbose_name', models.CharField(max_length=64, verbose_name='verbose name of field', default='', blank=True)),
                ('model_template', models.ForeignKey(verbose_name='model field', related_name='fields', to='model_creator.ModelTemplate')),
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
