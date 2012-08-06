# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EventType'
        db.create_table('sendgrid_eventtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('sendgrid', ['EventType'])

        # Adding model 'Event'
        db.create_table('sendgrid_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email_message', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sendgrid.EmailMessage'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sendgrid.EventType'])),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sendgrid', ['Event'])


    def backwards(self, orm):
        # Deleting model 'EventType'
        db.delete_table('sendgrid_eventtype')

        # Deleting model 'Event'
        db.delete_table('sendgrid_event')


    models = {
        'sendgrid.argument': {
            'Meta': {'object_name': 'Argument'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sendgrid.category': {
            'Meta': {'object_name': 'Category'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        'sendgrid.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
            'arguments': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sendgrid.Argument']", 'through': "orm['sendgrid.UniqueArgument']", 'symmetrical': 'False'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sendgrid.Category']", 'symmetrical': 'False'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'to_email': ('django.db.models.fields.CharField', [], {'max_length': '254'})
        },
        'sendgrid.emailmessageattachmentsdata': {
            'Meta': {'object_name': 'EmailMessageAttachmentsData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'attachments'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessagebccdata': {
            'Meta': {'object_name': 'EmailMessageBccData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'bcc'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessagebodydata': {
            'Meta': {'object_name': 'EmailMessageBodyData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'body'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessageccdata': {
            'Meta': {'object_name': 'EmailMessageCcData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'cc'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessageextraheadersdata': {
            'Meta': {'object_name': 'EmailMessageExtraHeadersData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'extra_headers'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessagesendgridheadersdata': {
            'Meta': {'object_name': 'EmailMessageSendGridHeadersData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'sendgrid_headers'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessagesubjectdata': {
            'Meta': {'object_name': 'EmailMessageSubjectData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'subject'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.emailmessagetodata': {
            'Meta': {'object_name': 'EmailMessageToData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'email_message': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'to'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['sendgrid.EmailMessage']"})
        },
        'sendgrid.event': {
            'Meta': {'object_name': 'Event'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.EmailMessage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.EventType']"})
        },
        'sendgrid.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'sendgrid.uniqueargument': {
            'Meta': {'object_name': 'UniqueArgument'},
            'argument': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.Argument']"}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email_message': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.EmailMessage']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['sendgrid']