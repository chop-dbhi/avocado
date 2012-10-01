# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataCategory'
        db.create_table('avocado_datacategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['avocado.DataCategory'])),
            ('order', self.gf('django.db.models.fields.FloatField')(null=True, db_column='_order', blank=True)),
        ))
        db.send_create_signal('avocado', ['DataCategory'])

        # Adding model 'DataField'
        db.create_table('avocado_datafield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name_plural', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('unit_plural', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.DataCategory'], null=True, blank=True)),
            ('enumerable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('searchable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('translator', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('data_modified', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('data_source', self.gf('django.db.models.fields.CharField')(max_length=250, null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fields+', null=True, to=orm['auth.Group'])),
            ('order', self.gf('django.db.models.fields.FloatField')(null=True, db_column='_order', blank=True)),
        ))
        db.send_create_signal('avocado', ['DataField'])

        # Adding unique constraint on 'DataField', fields ['app_name', 'model_name', 'field_name']
        db.create_unique('avocado_datafield', ['app_name', 'model_name', 'field_name'])

        # Adding M2M table for field sites on 'DataField'
        db.create_table('avocado_datafield_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datafield', models.ForeignKey(orm['avocado.datafield'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('avocado_datafield_sites', ['datafield_id', 'site_id'])

        # Adding model 'DataConcept'
        db.create_table('avocado_dataconcept', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name_plural', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.DataCategory'], null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='concepts+', null=True, to=orm['auth.Group'])),
            ('order', self.gf('django.db.models.fields.FloatField')(null=True, db_column='_order', blank=True)),
            ('formatter', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('queryview', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('avocado', ['DataConcept'])

        # Adding M2M table for field sites on 'DataConcept'
        db.create_table('avocado_dataconcept_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dataconcept', models.ForeignKey(orm['avocado.dataconcept'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('avocado_dataconcept_sites', ['dataconcept_id', 'site_id'])

        # Adding model 'DataConceptField'
        db.create_table('avocado_dataconceptfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='concept_fields', to=orm['avocado.DataField'])),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='concept_fields', to=orm['avocado.DataConcept'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name_plural', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.FloatField')(null=True, db_column='_order', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('avocado', ['DataConceptField'])

        # Adding model 'DataContext'
        db.create_table('avocado_datacontext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('json', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('composite', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('count', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='_count')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='datacontext+', null=True, to=orm['auth.User'])),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('avocado', ['DataContext'])

        # Adding model 'DataView'
        db.create_table('avocado_dataview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('archived', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('json', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
            ('session', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('count', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='_count')),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='dataview+', null=True, to=orm['auth.User'])),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal('avocado', ['DataView'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataField', fields ['app_name', 'model_name', 'field_name']
        db.delete_unique('avocado_datafield', ['app_name', 'model_name', 'field_name'])

        # Deleting model 'DataCategory'
        db.delete_table('avocado_datacategory')

        # Deleting model 'DataField'
        db.delete_table('avocado_datafield')

        # Removing M2M table for field sites on 'DataField'
        db.delete_table('avocado_datafield_sites')

        # Deleting model 'DataConcept'
        db.delete_table('avocado_dataconcept')

        # Removing M2M table for field sites on 'DataConcept'
        db.delete_table('avocado_dataconcept_sites')

        # Deleting model 'DataConceptField'
        db.delete_table('avocado_dataconceptfield')

        # Deleting model 'DataContext'
        db.delete_table('avocado_datacontext')

        # Deleting model 'DataView'
        db.delete_table('avocado_dataview')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'avocado.datacategory': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'DataCategory'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'_order'", 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['avocado.DataCategory']"}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'avocado.dataconcept': {
            'Meta': {'ordering': "('order',)", 'object_name': 'DataConcept'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.DataCategory']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'concepts'", 'symmetrical': 'False', 'through': "orm['avocado.DataConceptField']", 'to': "orm['avocado.DataField']"}),
            'formatter': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'concepts+'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_plural': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'_order'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'queryview': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'concepts+'", 'blank': 'True', 'to': "orm['sites.Site']"})
        },
        'avocado.dataconceptfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'DataConceptField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'concept_fields'", 'to': "orm['avocado.DataConcept']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'concept_fields'", 'to': "orm['avocado.DataField']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name_plural': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'_order'", 'blank': 'True'})
        },
        'avocado.datacontext': {
            'Meta': {'object_name': 'DataContext'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'composite': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'_count'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'datacontext+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'avocado.datafield': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_name', 'model_name', 'field_name'),)", 'object_name': 'DataField'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.DataCategory']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_modified': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'data_source': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enumerable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fields+'", 'null': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_plural': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'_order'", 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'searchable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'fields+'", 'blank': 'True', 'to': "orm['sites.Site']"}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'unit_plural': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'avocado.dataview': {
            'Meta': {'object_name': 'DataView'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'_count'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'dataview+'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['avocado']