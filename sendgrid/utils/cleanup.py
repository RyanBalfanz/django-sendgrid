import datetime
import logging
import time

from django.utils.timezone import now as now_utc

from sendgrid.models import EmailMessage, EmailMessageBodyData


ONE_DAY = datetime.timedelta(days=1)
ONE_WEEK = datetime.timedelta(weeks=1)

logger = logging.getLogger(__name__)

def delete_email_message_body_data(emailMessages):
	tick, tock = time.time(), None
	affectedEmailMessages = []
	unaffectedEmailMessages = []
	for emailMessage in emailMessages:
		try:
			bodyDataObject = emailMessage.body
		except EmailMessageBodyData.DoesNotExist:
			logger.info("EmailMessage {em} has no EmailMessageBodyData".format(em=emailMessage))
			unaffectedEmailMessages.append(emailMessage.id)
			continue
		else:
			bodyDataObject.delete()
			affectedEmailMessages.append(emailMessage.id)
	tock = time.time()

	summary = {
		"affected": affectedEmailMessages,
		"unaffected": unaffectedEmailMessages,
		"elapsedSeconds": tock - tick,
	}

	return summary

def cleanup_email_message_body_data(*args, **kwargs):
	"""
	Deletes ``EmailMessageBodyData`` objects created N {days|weeks} from now.

	>>> EmailMessage.objects.create()
	>>> EmailMessage.body = EmailMessageBodyData.objects.create(data="body")
	>>> EmailMessageBodyData.objects.count()
	1
	>>> cleanup_email_message_body_data(days=0)
	>>> EmailMessageBodyData.objects.count()
	1
	>>> cleanup_email_message_body_data(days=1)
	>>> EmailMessageBodyData.objects.count()
	0
	"""
	if all(kwargs.values()):
		# datetime.timedelta will actually handle multiple keyword args just fine
		raise Exception("Ambiguous arguments given")

	start = now_utc()
	delta = datetime.timedelta(**kwargs)
	purgeDate = start - delta
	logger.debug("Start: {s}".format(s=start))
	logger.debug("Delta: {d}".format(d=delta))
	logger.debug("Purge date: {p}".format(p=purgeDate))

	emailMessages = EmailMessage.objects.filter(
		creation_time__lt=purgeDate,
		body__isnull=False,
	)

	if emailMessages.exists():
		result = delete_email_message_body_data(emailMessages)
	else:
		result = None

	logger.debug("Result: {r}".format(r=str(result)))

	return result
