from __future__ import absolute_import

from collections import defaultdict

from django.core.mail import EmailMessage
from django.dispatch import receiver
from django.test import TestCase

from .mail import get_sendgrid_connection
from .mail import send_sendgrid_mail
from .message import SendGridEmailMessage
from .message import SendGridEmailMultiAlternatives
from .models import Argument
from .models import Category
from .models import Event, EmailMessage as EmailMessageModel
from .models import EventType
from .models import UniqueArgument
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

	def test_event_email_doesnt_exist(self):
		event_count = Event.objects.count()
		email_count = EmailMessageModel.objects.count()
		post_data = {
			"message_id": 'a5df', 
			"email" : self.email.from_email,
			"event" : "OPEN",
			}
		request = self.rf.post('/sendgrid/events',post_data)
		handle_single_event_request(request)
		#no event created
		self.assertEqual(Event.objects.count(),event_count)
		#no email created
		self.assertEqual(EmailMessageModel.objects.count(),email_count)

	def test_event_no_message_id(self):
		event_count = Event.objects.count()
		email_count = EmailMessageModel.objects.count()
		post_data = {
			"email" : self.email.from_email,
			"event" : "OPEN",
			}
		request = self.rf.post('/sendgrid/events',post_data)
		response = handle_single_event_request(request)
		#no event created
		self.assertEqual(Event.objects.count(),event_count)
		#no email created
		self.assertEqual(EmailMessageModel.objects.count(),email_count)


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
