import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as now_utc

from sendgrid.models import EmailMessage
from sendgrid.models import EmailMessageBodyData


ONE_DAY = datetime.timedelta(days=1)
ONE_WEEK = datetime.timedelta(weeks=1)

def filter_email_messages_created_before(start):
	return EmailMessage.objects.filter(
		creation_time__lt=start,
	)


class Command(BaseCommand):
	help = "Purges old EmailMessageBodyData objects"
	option_list = BaseCommand.option_list + (
	make_option("--as-date",
		default=False,
		action="store_true",
		help="Sets the number of days"
		),
	make_option("--fake",
		default=False,
		action="store_true",
		help="Fakes the operation"
		),
	make_option("--days",
		default=0,
		type="int",
		help="Sets the number of days"
		),
	make_option("--weeks",
		default=0,
		type="int",
		help="Sets the number of weeks"
		),
	)

	def handle(self, *args, **kwargs):
		nowUTC = now_utc()
		todayUTC = nowUTC.date()

		if all([kwargs["days"], kwargs["weeks"]]):
			raise CommandError("Ambiguous arguments given")

		if "days" in kwargs:
			delta = kwargs["days"]*ONE_DAY
			deltaType = "days"
		elif "weeks" in kwargs:
			delta = kwargs["weeks"]*ONE_WEEK
			deltaType = "weeks"
		else:
			raise CommandError

		purgeDate = nowUTC - delta
		if kwargs["as_date"] == True:
			purgeDate = purgeDate.date()

		emailMessages = filter_email_messages_created_before(purgeDate)
		numEmailMessages = emailMessages.count()

		prompt = "Delete {m} objects created before {date} ({n} {t} ago)?"
		print prompt.format(
			m=numEmailMessages,
			date=purgeDate,
			n=kwargs["days"] if deltaType == "days" else kwargs["weeks"],
			t=deltaType,
		)

		fake = kwargs["fake"]
		for emailMessage in emailMessages:
			try:
				bodyDataObject = emailMessage.body
			except EmailMessageBodyData.DoesNotExist:
				print "EmailMessage {em} has no EmailMessageBodyData".format(em=emailMessage)
				continue

			if not fake:
				bodyDataObject.delete()
			print "{prefix}Deleted body data for {em}".format(
				em=emailMessage,
				prefix="(FAKE) " if fake else ""
			)
