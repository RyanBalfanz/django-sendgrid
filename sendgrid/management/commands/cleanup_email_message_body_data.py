import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as now_utc

from sendgrid.models import EmailMessage
from sendgrid.models import EmailMessageBodyData
from sendgrid.utils.cleanup import cleanup_email_message_body_data
from sendgrid.utils.cleanup import delete_email_message_body_data

ONE_DAY = datetime.timedelta(days=1)
ONE_WEEK = datetime.timedelta(weeks=1)


class Command(BaseCommand):
	help = "Purges old EmailMessageBodyData objects"
	option_list = BaseCommand.option_list + (
	make_option("--as-date",
		default=False,
		action="store_true",
		help="Sets the number of days"
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
		days = kwargs.get("days", None)
		weeks = kwargs.get("weeks", None)
		return str(cleanup_email_message_body_data(days=days, weeks=weeks))
