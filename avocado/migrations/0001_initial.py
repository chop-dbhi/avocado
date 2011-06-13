# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('avocado_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('icon', self.gf('django.db.models.fields.files.FileField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('avocado', ['Category'])

        # Adding model 'Field'
        db.create_table(u'avocado_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chart_title', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('chart_yaxis', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('chart_xaxis', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('app_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('search_doc', self.gf('django.db.models.fields.TextField')(null=True, db_index=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'], null=True, blank=True)),
            ('translator', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enable_choices', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('choices_handler', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'avocado', ['Field'])

        # Adding unique constraint on 'Field', fields ['app_name', 'model_name', 'field_name']
        db.create_unique(u'avocado_field', ['app_name', 'model_name', 'field_name'])

        # Adding model 'Column'
        db.create_table('avocado_column', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.Category'], null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('search_doc', self.gf('django.db.models.fields.TextField')(null=True)),
            ('html_fmtr', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('csv_fmtr', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('avocado', ['Column'])

        # Adding model 'ColumnField'
        db.create_table('avocado_columnfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conceptfields', to=orm['avocado.Column'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.Field'])),
        ))
        db.send_create_signal('avocado', ['ColumnField'])

        # Adding model 'Criterion'
        db.create_table('avocado_criterion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.Category'], null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('search_doc', self.gf('django.db.models.fields.TextField')(null=True)),
            ('viewset', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('avocado', ['Criterion'])

        # Adding model 'CriterionField'
        db.create_table('avocado_criterionfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('concept', self.gf('django.db.models.fields.related.ForeignKey')(related_name='conceptfields', to=orm['avocado.Criterion'])),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['avocado.Field'])),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('avocado', ['CriterionField'])

        # Adding model 'Scope'
        db.create_table('avocado_scope', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('store', self.gf('avocado.store.fields.PickledField')(null=True, editable=False)),
            ('definition', self.gf('django.db.models.fields.TextField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 2, 25, 13, 14, 9, 564798))),
            ('cnt', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('avocado', ['Scope'])

        # Adding model 'Perspective'
        db.create_table('avocado_perspective', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('store', self.gf('avocado.store.fields.PickledField')(null=True, editable=False)),
            ('definition', self.gf('django.db.models.fields.TextField')(null=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 2, 25, 13, 14, 9, 564798))),
        ))
        db.send_create_signal('avocado', ['Perspective'])

        # Adding model 'Report'
        db.create_table('avocado_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('keywords', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('scope', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['avocado.Scope'], unique=True)),
            ('perspective', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['avocado.Perspective'], unique=True)),
        ))
        db.send_create_signal('avocado', ['Report'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Field', fields ['app_name', 'model_name', 'field_name']
        db.delete_unique(u'avocado_field', ['app_name', 'model_name', 'field_name'])

        # Deleting model 'Category'
        db.delete_table('avocado_category')

        # Deleting model 'Field'
        db.delete_table(u'avocado_field')

        # Deleting model 'Column'
        db.delete_table('avocado_column')

        # Deleting model 'ColumnField'
        db.delete_table('avocado_columnfield')

        # Deleting model 'Criterion'
        db.delete_table('avocado_criterion')

        # Deleting model 'CriterionField'
        db.delete_table('avocado_criterionfield')

        # Deleting model 'Scope'
        db.delete_table('avocado_scope')

        # Deleting model 'Perspective'
        db.delete_table('avocado_perspective')

        # Deleting model 'Report'
        db.delete_table('avocado_report')


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
        'avocado.category': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Category'},
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'avocado.column': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Column'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'csv_fmtr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['avocado.Field']", 'through': "orm['avocado.ColumnField']", 'symmetrical': 'False'}),
            'html_fmtr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        'avocado.columnfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ColumnField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conceptfields'", 'to': "orm['avocado.Column']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'avocado.criterion': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Criterion'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['avocado.Field']", 'through': "orm['avocado.CriterionField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'viewset': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'avocado.criterionfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CriterionField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conceptfields'", 'to': "orm['avocado.Criterion']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'avocado.field': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_name', 'model_name', 'field_name'),)", 'object_name': 'Field'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'chart_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'chart_xaxis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'chart_yaxis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'choices_handler': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enable_choices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_index': 'True'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'avocado.perspective': {
            'Meta': {'object_name': 'Perspective'},
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.PickledField', [], {'null': 'True', 'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 2, 25, 13, 14, 9, 564798)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.report': {
            'Meta': {'object_name': 'Report'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'perspective': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Perspective']", 'unique': 'True'}),
            'scope': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Scope']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.scope': {
            'Meta': {'object_name': 'Scope'},
            'cnt': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.PickledField', [], {'null': 'True', 'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 2, 25, 13, 14, 9, 564798)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['avocado']
