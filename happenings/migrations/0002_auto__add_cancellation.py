# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cancellation'
        db.create_table('happenings_cancellation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['happenings.Event'], related_name='cancellations')),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('happenings', ['Cancellation'])


    def backwards(self, orm):
        # Deleting model 'Cancellation'
        db.delete_table('happenings_cancellation')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'happenings.cancellation': {
            'Meta': {'object_name': 'Cancellation'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['happenings.Event']", 'related_name': "'cancellations'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'happenings.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'happenings.event': {
            'Meta': {'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {}),
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'eeeeee'", 'max_length': '10'}),
            'background_color_custom': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['happenings.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'events'"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'end_repeat': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'font_color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '10'}),
            'font_color_custom': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['happenings.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'repeat': ('django.db.models.fields.CharField', [], {'default': "'NEVER'", 'max_length': '15'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['happenings.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'happenings.location': {
            'Meta': {'object_name': 'Location'},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '31', 'blank': 'True'})
        },
        'happenings.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['happenings']