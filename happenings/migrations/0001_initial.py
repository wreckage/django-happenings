# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Event'
        db.create_table(u'happenings_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('all_day', self.gf('django.db.models.fields.BooleanField')()),
            ('repeat', self.gf('django.db.models.fields.CharField')(default='NEVER', max_length=15)),
            ('end_repeat', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='events', to=orm['auth.User'])),
            ('background_color', self.gf('django.db.models.fields.CharField')(default='eeeeee', max_length=10)),
            ('background_color_custom', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
            ('font_color', self.gf('django.db.models.fields.CharField')(default='000000', max_length=10)),
            ('font_color_custom', self.gf('django.db.models.fields.CharField')(max_length=6, blank=True)),
        ))
        db.send_create_signal(u'happenings', ['Event'])

        # Adding M2M table for field location on 'Event'
        m2m_table_name = db.shorten_name(u'happenings_event_location')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'happenings.event'], null=False)),
            ('location', models.ForeignKey(orm[u'happenings.location'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'location_id'])

        # Adding M2M table for field categories on 'Event'
        m2m_table_name = db.shorten_name(u'happenings_event_categories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'happenings.event'], null=False)),
            ('category', models.ForeignKey(orm[u'happenings.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'category_id'])

        # Adding M2M table for field tags on 'Event'
        m2m_table_name = db.shorten_name(u'happenings_event_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm[u'happenings.event'], null=False)),
            ('tag', models.ForeignKey(orm[u'happenings.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['event_id', 'tag_id'])

        # Adding model 'Location'
        db.create_table(u'happenings_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address_line_1', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address_line_2', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address_line_3', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=63, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=31, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=127, blank=True)),
        ))
        db.send_create_signal(u'happenings', ['Location'])

        # Adding model 'Category'
        db.create_table(u'happenings_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'happenings', ['Category'])

        # Adding model 'Tag'
        db.create_table(u'happenings_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'happenings', ['Tag'])


    def backwards(self, orm):
        # Deleting model 'Event'
        db.delete_table(u'happenings_event')

        # Removing M2M table for field location on 'Event'
        db.delete_table(db.shorten_name(u'happenings_event_location'))

        # Removing M2M table for field categories on 'Event'
        db.delete_table(db.shorten_name(u'happenings_event_categories'))

        # Removing M2M table for field tags on 'Event'
        db.delete_table(db.shorten_name(u'happenings_event_tags'))

        # Deleting model 'Location'
        db.delete_table(u'happenings_location')

        # Deleting model 'Category'
        db.delete_table(u'happenings_category')

        # Deleting model 'Tag'
        db.delete_table(u'happenings_tag')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'happenings.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'happenings.event': {
            'Meta': {'object_name': 'Event'},
            'all_day': ('django.db.models.fields.BooleanField', [], {}),
            'background_color': ('django.db.models.fields.CharField', [], {'default': "'eeeeee'", 'max_length': '10'}),
            'background_color_custom': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['happenings.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'events'", 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'end_repeat': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'font_color': ('django.db.models.fields.CharField', [], {'default': "'000000'", 'max_length': '10'}),
            'font_color_custom': ('django.db.models.fields.CharField', [], {'max_length': '6', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['happenings.Location']", 'symmetrical': 'False', 'blank': 'True'}),
            'repeat': ('django.db.models.fields.CharField', [], {'default': "'NEVER'", 'max_length': '15'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['happenings.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'happenings.location': {
            'Meta': {'object_name': 'Location'},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_3': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '127', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '63', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '31', 'blank': 'True'})
        },
        u'happenings.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['happenings']