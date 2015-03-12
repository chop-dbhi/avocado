# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import avocado.query.oldparsers.datacontext
import jsonfield.fields
from django.conf import settings
import avocado.query.oldparsers.dataview


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('published', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False, help_text='Note: archived takes precedence over being published')),
                ('order', models.FloatField(null=True, db_column=b'_order', blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='avocado.DataCategory', help_text=b'Sub-categories are limited to one-level deep', null=True)),
            ],
            options={
                'ordering': ('parent__order', 'parent__name', 'order', 'name'),
                'verbose_name_plural': 'data categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataConcept',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name_plural', models.CharField(max_length=200, null=True, blank=True)),
                ('published', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False, help_text='Note: archived takes precedence over being published')),
                ('type', models.CharField(max_length=100, null=True, blank=True)),
                ('order', models.FloatField(null=True, db_column=b'_order', blank=True)),
                ('formatter', models.CharField(blank=True, max_length=100, null=True, verbose_name=b'formatter', choices=[(b'Default', b'Default')])),
                ('viewable', models.BooleanField(default=True)),
                ('queryable', models.BooleanField(default=True)),
                ('sortable', models.BooleanField(default=True)),
                ('indexable', models.BooleanField(default=True)),
                ('category', models.ForeignKey(blank=True, to='avocado.DataCategory', null=True)),
            ],
            options={
                'ordering': ('category__order', 'category__name', 'order', 'name'),
                'permissions': (('view_dataconcept', 'Can view dataconcept'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataConceptField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('name_plural', models.CharField(max_length=100, null=True, blank=True)),
                ('order', models.FloatField(null=True, db_column=b'_order', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('concept', models.ForeignKey(related_name='concept_fields', to='avocado.DataConcept')),
            ],
            options={
                'ordering': ('order', 'name'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('json', jsonfield.fields.JSONField(default=dict, null=True, blank=True, validators=[avocado.query.oldparsers.datacontext.validate])),
                ('session', models.BooleanField(default=False)),
                ('template', models.BooleanField(default=False)),
                ('default', models.BooleanField(default=False)),
                ('session_key', models.CharField(max_length=40, null=True, blank=True)),
                ('accessed', models.DateTimeField(default=datetime.datetime(2015, 3, 10, 12, 40, 54, 775124), editable=False)),
                ('parent', models.ForeignKey(related_name='forks', blank=True, to='avocado.DataContext', null=True)),
                ('user', models.ForeignKey(related_name='datacontext+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name_plural', models.CharField(max_length=200, null=True, blank=True)),
                ('published', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False, help_text='Note: archived takes precedence over being published')),
                ('app_name', models.CharField(max_length=200)),
                ('model_name', models.CharField(max_length=200)),
                ('field_name', models.CharField(max_length=200)),
                ('label_field_name', models.CharField(help_text=b'Label field to the reference field', max_length=200, null=True, blank=True)),
                ('search_field_name', models.CharField(help_text=b'Search field to the reference field', max_length=200, null=True, blank=True)),
                ('order_field_name', models.CharField(help_text=b'Order field to the reference field', max_length=200, null=True, blank=True)),
                ('code_field_name', models.CharField(help_text=b'Order field to the reference field', max_length=200, null=True, blank=True)),
                ('unit', models.CharField(max_length=30, null=True, blank=True)),
                ('unit_plural', models.CharField(max_length=40, null=True, blank=True)),
                ('enumerable', models.BooleanField(default=False)),
                ('indexable', models.BooleanField(default=True)),
                ('type', models.CharField(help_text=b'Logical type of this field. Typically used downstream for defining behavior and semantics around the field.', max_length=100, null=True, blank=True)),
                ('translator', models.CharField(blank=True, max_length=100, null=True, choices=[(b'Default', b'Default')])),
                ('data_version', models.IntegerField(default=1, help_text=b'The current version of the underlying data for this field as of the last modification/update.')),
                ('order', models.FloatField(null=True, db_column=b'_order', blank=True)),
                ('category', models.ForeignKey(blank=True, to='avocado.DataCategory', null=True)),
                ('sites', models.ManyToManyField(related_name='fields+', to='sites.Site', blank=True)),
            ],
            options={
                'ordering': ('category__order', 'category__name', 'order', 'name'),
                'permissions': (('view_datafield', 'Can view datafield'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataQuery',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('session', models.BooleanField(default=False)),
                ('template', models.BooleanField(default=False)),
                ('default', models.BooleanField(default=False)),
                ('session_key', models.CharField(max_length=40, null=True, blank=True)),
                ('accessed', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('public', models.BooleanField(default=False)),
                ('context_json', jsonfield.fields.JSONField(default=dict, null=True, blank=True, validators=[avocado.query.oldparsers.datacontext.validate])),
                ('view_json', jsonfield.fields.JSONField(default=dict, null=True, blank=True, validators=[avocado.query.oldparsers.dataview.validate])),
                ('parent', models.ForeignKey(related_name='forks', blank=True, to='avocado.DataQuery', null=True)),
                ('shared_users', models.ManyToManyField(related_name='shareddataquery+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='dataquery+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name_plural': 'data queries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('keywords', models.CharField(max_length=100, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('json', jsonfield.fields.JSONField(default=dict, null=True, blank=True, validators=[avocado.query.oldparsers.dataview.validate])),
                ('session', models.BooleanField(default=False)),
                ('template', models.BooleanField(default=False)),
                ('default', models.BooleanField(default=False)),
                ('session_key', models.CharField(max_length=40, null=True, blank=True)),
                ('accessed', models.DateTimeField(default=datetime.datetime(2015, 3, 10, 12, 40, 54, 776427), editable=False)),
                ('parent', models.ForeignKey(related_name='forks', blank=True, to='avocado.DataView', null=True)),
                ('user', models.ForeignKey(related_name='dataview+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('event', models.CharField(max_length=200)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('session_key', models.CharField(max_length=40, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('user', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('data', jsonfield.fields.JSONField(null=True, blank=True)),
                ('session_key', models.CharField(max_length=40, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now, db_index=True)),
                ('deleted', models.BooleanField(default=False)),
                ('changes', jsonfield.fields.JSONField(null=True, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='+revision', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-timestamp',),
                'get_latest_by': 'timestamp',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='datafield',
            unique_together=set([('app_name', 'model_name', 'field_name')]),
        ),
        migrations.AddField(
            model_name='dataconceptfield',
            name='field',
            field=models.ForeignKey(related_name='concept_fields', to='avocado.DataField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataconcept',
            name='fields',
            field=models.ManyToManyField(related_name='concepts', through='avocado.DataConceptField', to='avocado.DataField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dataconcept',
            name='sites',
            field=models.ManyToManyField(related_name='concepts+', to='sites.Site', blank=True),
            preserve_default=True,
        ),
    ]
