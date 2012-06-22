# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailMessage'
        db.create_table('sendgrid_emailmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message_id', self.gf('django.db.models.fields.CharField')(max_length=36, unique=True, null=True, blank=True)),
            ('from_email', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('to_email', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('response', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sendgrid', ['EmailMessage'])

        # Adding model 'EmailMessageSubjectData'
        db.create_table('sendgrid_emailmessagesubjectdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='subject', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageSubjectData'])

        # Adding model 'EmailMessageSendGridHeadersData'
        db.create_table('sendgrid_emailmessagesendgridheadersdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='sendgrid_headers', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageSendGridHeadersData'])

        # Adding model 'EmailMessageExtraHeadersData'
        db.create_table('sendgrid_emailmessageextraheadersdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='extra_headers', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageExtraHeadersData'])

        # Adding model 'EmailMessageBodyData'
        db.create_table('sendgrid_emailmessagebodydata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='body', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageBodyData'])

        # Adding model 'EmailMessageAttachmentsData'
        db.create_table('sendgrid_emailmessageattachmentsdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='attachments', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageAttachmentsData'])

        # Adding model 'EmailMessageBccData'
        db.create_table('sendgrid_emailmessagebccdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='bcc', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageBccData'])

        # Adding model 'EmailMessageCcData'
        db.create_table('sendgrid_emailmessageccdata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='cc', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageCcData'])

        # Adding model 'EmailMessageToData'
        db.create_table('sendgrid_emailmessagetodata', (
            ('email_message', self.gf('django.db.models.fields.related.OneToOneField')(related_name='to', unique=True, primary_key=True, to=orm['sendgrid.EmailMessage'])),
            ('data', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['EmailMessageToData'])


    def backwards(self, orm):
        # Deleting model 'EmailMessage'
        db.delete_table('sendgrid_emailmessage')

        # Deleting model 'EmailMessageSubjectData'
        db.delete_table('sendgrid_emailmessagesubjectdata')

        # Deleting model 'EmailMessageSendGridHeadersData'
        db.delete_table('sendgrid_emailmessagesendgridheadersdata')

        # Deleting model 'EmailMessageExtraHeadersData'
        db.delete_table('sendgrid_emailmessageextraheadersdata')

        # Deleting model 'EmailMessageBodyData'
        db.delete_table('sendgrid_emailmessagebodydata')

        # Deleting model 'EmailMessageAttachmentsData'
        db.delete_table('sendgrid_emailmessageattachmentsdata')

        # Deleting model 'EmailMessageBccData'
        db.delete_table('sendgrid_emailmessagebccdata')

        # Deleting model 'EmailMessageCcData'
        db.delete_table('sendgrid_emailmessageccdata')

        # Deleting model 'EmailMessageToData'
        db.delete_table('sendgrid_emailmessagetodata')


    models = {
        'sendgrid.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'to_email': ('django.db.models.fields.CharField', [], {'max_length': '150'})
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