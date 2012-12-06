from __future__ import absolute_import

import json
from collections import defaultdict

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.test import TestCase
from django.test.client import Client
from django.utils.http import urlencode

from .constants import BATCHED_EVENT_SEPARATOR, EVENT_TYPES_EXTRA_FIELDS_MAP, EVENT_MODEL_NAMES, UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID
from .mail import get_sendgrid_connection
from .mail import send_sendgrid_mail
from .message import SendGridEmailMessage
from .message import SendGridEmailMultiAlternatives
from .models import Argument
from .models import Category
from .models import Event, ClickEvent, BounceEvent, DeferredEvent, DroppedEvent, DeliverredEvent, EmailMessage as EmailMessageModel
from .models import EmailMessageAttachmentsData
from .models import EventType
from .models import UniqueArgument
from .settings import SENDGRID_CREATE_MISSING_EMAIL_MESSAGES
from .signals import sendgrid_email_sent
from .utils import filterutils
# from .utils import get_email_message
from .utils import in_test_environment
from .utils.requestfactory import RequestFactory 
from .views import handle_single_event_request


TEST_SENDER_EMAIL = "ryan@example.com"
TEST_RECIPIENTS = ["ryan@example.com"]

validate_filter_setting_value = filterutils.validate_filter_setting_value
validate_filter_specification = filterutils.validate_filter_specification
update_filters = filterutils.update_filters


class SendGridBatchedEventTest(TestCase):
	def setUp(self):
		self.email1 = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		self.email1.send()
		self.email2 = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		self.email2.send()
		self.client = Client()

		self.events = [
			{
				"email": TEST_RECIPIENTS[0],
				"timestamp": 1322000095,
				"message_id": str(self.email1.message_id),
				"event": "OPEN"
			},
			{
				"email": TEST_RECIPIENTS[0],
				"timestamp": 1322000096,
				"message_id": str(self.email2.message_id),
				"event": "DELIVERED"
			},
			{
				"email": TEST_RECIPIENTS[0],
				"timestamp": 1322000097,
				"message_id": str(self.email2.message_id),
				"event": "OPEN"
			}
		]

	def test_batched_events_emails_exist(self):
		postData = BATCHED_EVENT_SEPARATOR.join(json.dumps(event, separators=(",", ":")) for event in self.events)
		self.client.post(reverse("sendgrid_post_event"), content_type="application/json", data=postData)
		self.assertEqual(Event.objects.count(), len(self.events))


class SendGridEventTest(TestCase):
	def setUp(self):
		self.email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		self.email.send()
		self.rf = RequestFactory()

	def test_event_email_exists(self):
		event_count = Event.objects.count()
		post_data = {
			"message_id": self.email.message_id, 
			"email" : self.email.from_email,
			"event" : "OPEN",
		}
		request = self.rf.post('/sendgrid/events',post_data)
		handle_single_event_request(request)
		#Event created
		self.assertEqual(Event.objects.count(),event_count+1)
		#Email matches original message_id
		self.assertEqual(Event.objects.get().email_message.message_id, self.email.message_id.__str__())

	def verify_event_with_missing_email(self,post_data):
		event_count = Event.objects.count()
		email_count = EmailMessageModel.objects.count()

		for key in UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID:
			post_data[key] = key+"_value"

		request = self.rf.post('/sendgrid/events',post_data)
		handle_single_event_request(request)

		if SENDGRID_CREATE_MISSING_EMAIL_MESSAGES:
			delta = 1
		else:
			delta = 0

		#event created
		self.assertEqual(Event.objects.count(), event_count + delta)
		#email created
		self.assertEqual(EmailMessageModel.objects.count(), email_count + delta)

		if SENDGRID_CREATE_MISSING_EMAIL_MESSAGES:
			event = Event.objects.get(email=post_data['email'])
			emailMessage = event.email_message
			#check to_email
			self.assertEqual(event.email_message.to_email, event.email)

			#check unique args
			for key in UNIQUE_ARGS_STORED_FOR_EVENTS_WITHOUT_MESSAGE_ID:
				self.assertEqual(post_data[key],emailMessage.uniqueargument_set.get(argument__key=key).data)

			#post another event
			request = self.rf.post('/sendgrid/events',post_data)
			response = handle_single_event_request(request)

			#should be same email_count
			self.assertEqual(EmailMessageModel.objects.count(),email_count + 1)

	def test_event_email_doesnt_exist(self):
		postData = {
			"message_id": 'a5df', 
			"email" : self.email.to[0],
			"event" : "OPEN",
			"category": ["test_category", "another_test_category"],
		}

		self.verify_event_with_missing_email(postData)

	def test_event_no_message_id(self):
		postData = {
			"email" : self.email.to[0],
			"event" : "OPEN",
			"category": "test_category",
		}
		self.verify_event_with_missing_email(postData)

	def test_event_email_doesnt_exist_no_category(self):
		postData = {
			"message_id": 'a5df', 
			"email" : self.email.to[0],
			"event" : "OPEN"
		}

		self.verify_event_with_missing_email(postData)


class SendGridEmailTest(TestCase):
	"""docstring for SendGridEmailTest"""
	def test_email_has_unique_id(self):
		"""
		Tests the existence of the ``SendGridEmailMessage._message_id`` attribute.
		"""
		email = SendGridEmailMessage()
		self.assertTrue(email._message_id)
		
	def test_email_sends_unique_id(self):
		"""
		Tests sending a ``SendGridEmailMessage`` adds a ``message_id`` to the unique args.
		"""
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		self.assertTrue(email.sendgrid_headers.data["unique_args"]["message_id"])
		
	def test_unique_args_persist(self):
		"""
		Tests that unique args are not lost due to sending adding the ``message_id`` arg.
		"""
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		uniqueArgs = {
			"unique_arg_1": 1,
			"unique_arg_2": 2,
			"unique_arg_3": 3,
		}
		email.sendgrid_headers.setUniqueArgs(uniqueArgs)
		email.send()

		for k, v in uniqueArgs.iteritems():
			self.assertEqual(v, email.sendgrid_headers.data["unique_args"][k])

		self.assertTrue(email.sendgrid_headers.data["unique_args"]["message_id"])

	def test_email_sent_signal_has_message(self):
		"""
		Tests the existence of the ``message`` keywork arg from the ``sendgrid_email_sent`` signal.
		"""
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.assertTrue("response" in kwargs)
			self.assertTrue("message" in kwargs)
			
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		response = email.send()


class SendGridInTestEnvTest(TestCase):
	def test_in_test_environment(self):
		"""
		Tests that the test environment is detected.
		"""
		self.assertEqual(in_test_environment(), True)


class SendWithSendGridEmailMessageTest(TestCase):
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.signalsReceived = defaultdict(list)
		
	def test_send_email_sends_signal(self):
		"""
		Tests that sending a ``SendGridEmailMessage`` sends a ``sendgrid_email_sent`` signal.
		"""
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.signalsReceived["sendgrid_email_sent"].append(1)
			return True
			
		email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		
		numEmailSentSignalsRecieved = sum(self.signalsReceived["sendgrid_email_sent"])
		self.assertEqual(numEmailSentSignalsRecieved, 1)
		
	def test_send_with_send_mail(self):
		"""
		Tests sending an email with the ``send_email_with_sendgrid`` helper.
		"""
		send_sendgrid_mail(
			subject="Your new account!",
			message="Thanks for signing up.",
			from_email='welcome@example.com',
			recipient_list=['ryan@example.com'],
		)


class SendWithEmailMessageTest(TestCase):
	"""docstring for SendWithEmailMessageTest"""
	def setUp(self):
		"""
		Sets up the tests.
		"""
		self.connection = get_sendgrid_connection()
		
	def test_send_with_email_message(self):
		"""
		Tests sending an ``EmailMessage`` with the ``SendGridEmailBackend``.
		"""
		email = EmailMessage(
			subject="Your new account!",
			body="Thanks for signing up.",
			from_email='welcome@example.com',
			to=['ryan@example.com'],
			connection=self.connection,
		)
		email.send()



class SendWithSendGridEmailMultiAlternativesTest(TestCase):
	def setUp(self):
		self.signalsReceived = defaultdict(list)
		
	def test_send_multipart_email(self):
		"""
		Tests sending multipart emails.
		"""
		subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
		text_content = 'This is an important message.'
		html_content = '<p>This is an <strong>important</strong> message.</p>'
		msg = SendGridEmailMultiAlternatives(subject, text_content, from_email, [to])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
		
	def test_send_multipart_email_sends_signal(self):
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			self.signalsReceived["sendgrid_email_sent"].append(1)
			return True
			
		email = SendGridEmailMultiAlternatives(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		email.send()
		
		numEmailSentSignalsRecieved = sum(self.signalsReceived["sendgrid_email_sent"])
		self.assertEqual(numEmailSentSignalsRecieved, 1)


class FilterUtilsTests(TestCase):
	"""docstring for FilterUtilsTests"""
	def setUp(self):
		"""
		Set up the tests.
		"""
		pass
		
	def test_validate_filter_spec(self):
		"""
		Tests validation of a filter specification.
		"""
		filterSpec = {
			"subscriptiontrack": {
				"enable": 1,
			},
			"opentrack": {
				"enable": 0,
			},
		}
		self.assertEqual(validate_filter_specification(filterSpec), True)
		
	def test_subscriptiontrack_enable_parameter(self):
		"""
		Tests the ``subscriptiontrack`` filter's ``enable`` paramter.
		"""
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 1), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 0.0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", 1.0), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "0"), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "1"), True)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "0.0"), False)
		self.assertEqual(validate_filter_setting_value("subscriptiontrack", "enable", "1.0"), False)
		
	def test_opentrack_enable_parameter(self):
		"""
		Tests the ``opentrack`` filter's ``enable`` paramter.
		"""
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 1), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 0.0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", 1.0), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "0"), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "1"), True)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "0.0"), False)
		self.assertEqual(validate_filter_setting_value("opentrack", "enable", "1.0"), False)


class UpdateFiltersTests(TestCase):
	"""docstring for SendWithFiltersTests"""
	def setUp(self):
		"""docstring for setUp"""
		self.email = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		
	def test_update_filters(self):
		"""
		Tests SendGrid filter functionality.
		"""
		filterSpec = {
			"subscriptiontrack": {
				"enable": 1,
			},
			"opentrack": {
				"enable": 0,
			},
		}
		update_filters(self.email, filterSpec)
		self.email.send()


# class TestGetEmailMessageUtil(TestCase):
# 	"""docstring for TestGetEmailMessageUtil"""
# 	def test_get_with_email_message(self):
# 		from .models import EmailMessage as SGEmailMessage

# 		original = SGEmailMessage.objects.create()
# 		result = get_email_message(original)
# 		self.assertEqual(original, result)

# 	def test_get_with_id(self):
# 		from .models import EmailMessage as SGEmailMessage

# 		original = SGEmailMessage.objects.create()
# 		result = get_email_message(original.id)
# 		self.assertEqual(original, result)

# 	def test_with_message_id(self):
# 		from sendgrid.models import EmailMessage as SGEmailMessage

# 		original = SGEmailMessage.objects.create()
# 		result = get_email_message(original.message_id)
# 		self.assertEqual(original, result)


class CategoryTests(TestCase):
	def setUp(self):
		self.testCategoryNames = (
			"Test Category 1",
			"Test Category 2",
		)

	def assert_category_exists(self, categoryName):
		category = Category.objects.get(name=categoryName)
		return category

	def test_send_with_single_category(self):
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			emailMessage = kwargs["message"]
			sendgridHeadersData = emailMessage.sendgrid_headers.data

			expectedCategory = self.testCategoryNames[0]
			self.assertEqual(sendgridHeadersData["category"], expectedCategory)

		sendgridEmailMessage = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		sendgridEmailMessage.sendgrid_headers.setCategory(self.testCategoryNames[0])
		sendgridEmailMessage.update_headers()
		sendgridEmailMessage.send()

		category = self.assert_category_exists(self.testCategoryNames[0])
		self.assertTrue(category)

	def test_send_with_multiple_categories(self):
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			emailMessage = kwargs["message"]
			sendgridHeadersData = emailMessage.sendgrid_headers.data

			expectedCategories = self.testCategoryNames
			self.assertEqual(sendgridHeadersData["category"], expectedCategories)

		sendgridEmailMessage = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		sendgridEmailMessage.sendgrid_headers.setCategory(self.testCategoryNames)
		sendgridEmailMessage.update_headers()
		sendgridEmailMessage.send()

		for category in self.testCategoryNames:
			category = self.assert_category_exists(self.testCategoryNames[0])
			self.assertTrue(category)


class UniqueArgumentTests(TestCase):
	def setUp(self):
		pass

	def assert_argument_exists(self, argumentName):
		argument = Argument.objects.get(key=argumentName)
		return argument

	def assert_unique_argument_exists(self, key, value):
		uniqueArgument = UniqueArgument.objects.get(
			argument=Argument.objects.get(key=key),
			data=value
		)
		return uniqueArgument

	def test_send_with_unique_arguments(self):
		@receiver(sendgrid_email_sent)
		def receive_sendgrid_email_sent(*args, **kwargs):
			"""
			Receives sendgrid_email_sent signals.
			"""
			emailMessage = kwargs["message"]
			sendgridHeadersData = emailMessage.sendgrid_headers.data

			self.assertTrue(sendgridHeadersData["unique_args"])

		sendgridEmailMessage = SendGridEmailMessage(to=TEST_RECIPIENTS, from_email=TEST_SENDER_EMAIL)
		# sendgridEmailMessage.sendgrid_headers.setCategory(self.testCategoryNames[0])
		# sendgridEmailMessage.update_headers()
		sendgridEmailMessage.send()

		argument = self.assert_argument_exists("message_id")
		self.assertTrue(argument)

		expectedUniqueArgKeyValue = {
			"key": "message_id",
			"value": sendgridEmailMessage.message_id,
		}
		uniqueArgument = self.assert_unique_argument_exists(**expectedUniqueArgKeyValue)
		self.assertTrue(uniqueArgument)

from .utils.testutils import post_test_event
class EventPostTests(TestCase):
	fixtures = ["initial_data.json"]

	def setUp(self):
		self.client = Client()
		self.email_message = EmailMessageModel.objects.create(to_email=TEST_RECIPIENTS[0], from_email=TEST_SENDER_EMAIL,message_id='123abc')

	def test_all_event_types(self):
		"""
		Tests all event types listed in EVENT_MODEL_NAMES
		Checks that every EXTRA_FIELD is saved
		"""
		for event_type, event_model_name in EVENT_MODEL_NAMES.items():
			print "Testing {0} event".format(event_type)
			event_model = eval(EVENT_MODEL_NAMES[event_type]) if event_type in EVENT_MODEL_NAMES.keys() else Event
			event_count_before = event_model.objects.count()
			response = post_test_event(event_type,event_model_name,self.email_message)
			self.assertEqual(event_model.objects.count(),event_count_before+1)
			event = event_model.objects.filter(event_type__name=event_type)[0]
			for key in EVENT_TYPES_EXTRA_FIELDS_MAP[event_type.upper()]:
				self.assertNotEqual(event.__getattribute__(key),None)

class EventTypeFixtureTests(TestCase):
	fixtures = ["initial_data.json"]

	def setUp(self):
		self.expectedEventTypes = {
			"UNKNOWN": 1,
			"DEFERRED": 2,
			"PROCESSED": 3,
			"DROPPED": 4,
			"DELIVERED": 5,
			"BOUNCE": 6,
			"OPEN": 7,
			"CLICK": 8,
			"SPAMREPORT": 9,
			"UNSUBSCRIBE": 10,
		}

	def test_event_types_exists(self):
		for name, primaryKey in self.expectedEventTypes.iteritems():
			self.assertEqual(
				EventType.objects.get(pk=primaryKey),
				EventType.objects.get(name=name)
			)


class DownloadAttachmentTestCase(TestCase):
	def setUp(self):

		self.attachments = {
			"file1.csv": "name,age\r\nryan,28",
			# "file2.csv": "name,age\r\nryan,28"
		}

		emailMessage = SendGridEmailMessage(
			to=TEST_RECIPIENTS,
			from_email=TEST_SENDER_EMAIL)
		for name, contents in self.attachments.iteritems():
			emailMessage.attach(name, contents)

		response = emailMessage.send()
		self.assertEqual(response, 1)
		self.assertEqual(EmailMessageModel.objects.count(), 1)
		self.assertEqual(EmailMessageAttachmentsData.objects.count(), 1)

	def test_attachments_exist_for_email_message(self):
		em = EmailMessageModel.objects.get(id=1)
		emailMessageAttachments = em.attachments
		self.assertEqual(len(eval(emailMessageAttachments.data)), len(self.attachments))

	def test_download_attachments(self):
		em = EmailMessageModel.objects.get(id=1)
		attachmentsURL = reverse("sendgrid_download_attachments", args=(em.message_id,))
		c = Client()
		response = c.get(attachmentsURL)
		self.assertEqual(response.status_code, 200)

class DownloadAttachment404TestCase(TestCase):
	def setUp(self):
		emailMessage = SendGridEmailMessage(
			to=TEST_RECIPIENTS,
			from_email=TEST_SENDER_EMAIL)

		response = emailMessage.send()
		self.assertEqual(response, 1)
		self.assertEqual(EmailMessageModel.objects.count(), 1)
		self.assertEqual(EmailMessageAttachmentsData.objects.count(), 0)

	def test_attachments_exist_for_email_message(self):
		em = EmailMessageModel.objects.get(id=1)
		emailMessageAttachments = em.attachments_data
		self.assertEqual(emailMessageAttachments, None)

	def test_download_attachments(self):
		em = EmailMessageModel.objects.get(id=1)
		attachmentsURL = reverse("sendgrid_download_attachments", args=(em.message_id,))
		c = Client()
		response = c.get(attachmentsURL)
		self.assertEqual(response.status_code, 404)
