# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BounceType'
        db.create_table('sendgrid_bouncetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('sendgrid', ['BounceType'])

        # Adding model 'DroppedEvent'
        db.create_table('sendgrid_droppedevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sendgrid.Event'], unique=True, primary_key=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('sendgrid', ['DroppedEvent'])

        # Adding model 'BounceReason'
        db.create_table('sendgrid_bouncereason', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reason', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['BounceReason'])

        # Adding model 'ClickUrl'
        db.create_table('sendgrid_clickurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['ClickUrl'])

        # Adding model 'DeferredEvent'
        db.create_table('sendgrid_deferredevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sendgrid.Event'], unique=True, primary_key=True)),
            ('response', self.gf('django.db.models.fields.TextField')()),
            ('attempt', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('sendgrid', ['DeferredEvent'])

        # Adding model 'DeliverredEvent'
        db.create_table('sendgrid_deliverredevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sendgrid.Event'], unique=True, primary_key=True)),
            ('response', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sendgrid', ['DeliverredEvent'])

        # Adding model 'BounceEvent'
        db.create_table('sendgrid_bounceevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sendgrid.Event'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('bounce_reason', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sendgrid.BounceReason'])),
            ('bounce_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sendgrid.BounceType'])),
        ))
        db.send_create_signal('sendgrid', ['BounceEvent'])

        # Adding model 'ClickEvent'
        db.create_table('sendgrid_clickevent', (
            ('event_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sendgrid.Event'], unique=True, primary_key=True)),
            ('click_url', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sendgrid.ClickUrl'])),
        ))
        db.send_create_signal('sendgrid', ['ClickEvent'])


    def backwards(self, orm):
        # Deleting model 'BounceType'
        db.delete_table('sendgrid_bouncetype')

        # Deleting model 'DroppedEvent'
        db.delete_table('sendgrid_droppedevent')

        # Deleting model 'BounceReason'
        db.delete_table('sendgrid_bouncereason')

        # Deleting model 'ClickUrl'
        db.delete_table('sendgrid_clickurl')

        # Deleting model 'DeferredEvent'
        db.delete_table('sendgrid_deferredevent')

        # Deleting model 'DeliverredEvent'
        db.delete_table('sendgrid_deliverredevent')

        # Deleting model 'BounceEvent'
        db.delete_table('sendgrid_bounceevent')

        # Deleting model 'ClickEvent'
        db.delete_table('sendgrid_clickevent')


    models = {
        'sendgrid.argument': {
            'Meta': {'object_name': 'Argument'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'sendgrid.bounceevent': {
            'Meta': {'object_name': 'BounceEvent', '_ormbases': ['sendgrid.Event']},
            'bounce_reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.BounceReason']"}),
            'bounce_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.BounceType']"}),
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sendgrid.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'sendgrid.bouncereason': {
            'Meta': {'object_name': 'BounceReason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {})
        },
        'sendgrid.bouncetype': {
            'Meta': {'object_name': 'BounceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'sendgrid.category': {
            'Meta': {'object_name': 'Category'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'})
        },
        'sendgrid.clickevent': {
            'Meta': {'object_name': 'ClickEvent', '_ormbases': ['sendgrid.Event']},
            'click_url': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.ClickUrl']"}),
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sendgrid.Event']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sendgrid.clickurl': {
            'Meta': {'object_name': 'ClickUrl'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        'sendgrid.deferredevent': {
            'Meta': {'object_name': 'DeferredEvent', '_ormbases': ['sendgrid.Event']},
            'attempt': ('django.db.models.fields.IntegerField', [], {}),
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sendgrid.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {})
        },
        'sendgrid.deliverredevent': {
            'Meta': {'object_name': 'DeliverredEvent', '_ormbases': ['sendgrid.Event']},
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sendgrid.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {})
        },
        'sendgrid.droppedevent': {
            'Meta': {'object_name': 'DroppedEvent', '_ormbases': ['sendgrid.Event']},
            'event_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sendgrid.Event']", 'unique': 'True', 'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sendgrid.EventType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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