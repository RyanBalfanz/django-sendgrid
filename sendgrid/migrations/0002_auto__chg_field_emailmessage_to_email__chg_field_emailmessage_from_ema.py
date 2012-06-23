# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'EmailMessage.to_email'
        db.alter_column('sendgrid_emailmessage', 'to_email', self.gf('django.db.models.fields.CharField')(max_length=254))

        # Changing field 'EmailMessage.from_email'
        db.alter_column('sendgrid_emailmessage', 'from_email', self.gf('django.db.models.fields.CharField')(max_length=254))

    def backwards(self, orm):

        # Changing field 'EmailMessage.to_email'
        db.alter_column('sendgrid_emailmessage', 'to_email', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'EmailMessage.from_email'
        db.alter_column('sendgrid_emailmessage', 'from_email', self.gf('django.db.models.fields.CharField')(max_length=150))

    models = {
        'sendgrid.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
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
        }
    }

    complete_apps = ['sendgrid']