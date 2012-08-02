# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('sendgrid_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('sendgrid', ['Category'])

        # Adding M2M table for field categories on 'EmailMessage'
        db.create_table('sendgrid_emailmessage_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('emailmessage', models.ForeignKey(orm['sendgrid.emailmessage'], null=False)),
            ('category', models.ForeignKey(orm['sendgrid.category'], null=False))
        ))
        db.create_unique('sendgrid_emailmessage_categories', ['emailmessage_id', 'category_id'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('sendgrid_category')

        # Removing M2M table for field categories on 'EmailMessage'
        db.delete_table('sendgrid_emailmessage_categories')


    models = {
        'sendgrid.category': {
            'Meta': {'object_name': 'Category'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        'sendgrid.emailmessage': {
            'Meta': {'object_name': 'EmailMessage'},
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
        }
    }

    complete_apps = ['sendgrid']