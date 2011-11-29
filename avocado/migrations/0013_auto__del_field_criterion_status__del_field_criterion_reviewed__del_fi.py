# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Criterion.status'
        db.delete_column('avocado_criterion', 'status')

        # Deleting field 'Criterion.reviewed'
        db.delete_column('avocado_criterion', 'reviewed')

        # Deleting field 'Criterion.note'
        db.delete_column('avocado_criterion', 'note')

        # Deleting field 'Column.status'
        db.delete_column('avocado_column', 'status')

        # Deleting field 'Column.reviewed'
        db.delete_column('avocado_column', 'reviewed')

        # Deleting field 'Column.note'
        db.delete_column('avocado_column', 'note')

        # Deleting field 'Field.status'
        db.delete_column('avocado_field', 'status')

        # Deleting field 'Field.note'
        db.delete_column('avocado_field', 'note')

        # Deleting field 'Field.reviewed'
        db.delete_column('avocado_field', 'reviewed')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'Criterion.status'
        raise RuntimeError("Cannot reverse this migration. 'Criterion.status' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Criterion.reviewed'
        raise RuntimeError("Cannot reverse this migration. 'Criterion.reviewed' and its values cannot be restored.")

        # Adding field 'Criterion.note'
        db.add_column('avocado_criterion', 'note', self.gf('django.db.models.fields.TextField')(null=True), keep_default=False)

        # User chose to not deal with backwards NULL issues for 'Column.status'
        raise RuntimeError("Cannot reverse this migration. 'Column.status' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Column.reviewed'
        raise RuntimeError("Cannot reverse this migration. 'Column.reviewed' and its values cannot be restored.")

        # Adding field 'Column.note'
        db.add_column('avocado_column', 'note', self.gf('django.db.models.fields.TextField')(null=True), keep_default=False)

        # Adding field 'Field.status'
        db.add_column('avocado_field', 'status', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True), keep_default=False)

        # Adding field 'Field.note'
        db.add_column('avocado_field', 'note', self.gf('django.db.models.fields.TextField')(null=True), keep_default=False)

        # Adding field 'Field.reviewed'
        db.add_column('avocado_field', 'reviewed', self.gf('django.db.models.fields.DateTimeField')(null=True), keep_default=False)


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
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['avocado.Category']"})
        },
        'avocado.column': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Column'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'csv_fmtr': ('django.db.models.fields.CharField', [], {'default': "'Default'", 'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['avocado.Field']", 'through': "orm['avocado.ColumnField']", 'symmetrical': 'False'}),
            'html_fmtr': ('django.db.models.fields.CharField', [], {'default': "'Default'", 'max_length': '100'}),
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
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'avocado.criterion': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Criterion'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['avocado.Field']", 'through': "orm['avocado.CriterionField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'viewset': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100'})
        },
        'avocado.criterionfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CriterionField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conceptfields'", 'to': "orm['avocado.Criterion']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'avocado.field': {
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
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'avocado.perspective': {
            'Meta': {'object_name': 'Perspective'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Perspective']", 'null': 'True'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'store': ('avocado.store.fields.JSONField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'avocado.report': {
            'Meta': {'object_name': 'Report'},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'cnt'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'perspective': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Perspective']", 'unique': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Report']", 'null': 'True'}),
            'scope': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Scope']", 'unique': 'True'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'avocado.scope': {
            'Meta': {'object_name': 'Scope'},
            'count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'cnt'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'reference': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Scope']", 'null': 'True'}),
            'session': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'store': ('avocado.store.fields.JSONField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
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
