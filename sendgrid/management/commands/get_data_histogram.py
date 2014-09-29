from __future__ import print_function

import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now as now_utc

from sendgrid.models import EmailMessage
from sendgrid.models import EmailMessageAttachmentsData
from sendgrid.models import EmailMessageBodyData
from sendgrid.models import EmailMessageBccData
from sendgrid.models import EmailMessageCcData
from sendgrid.models import EmailMessageExtraHeadersData
from sendgrid.models import EmailMessageSendGridHeadersData
from sendgrid.models import EmailMessageSubjectData
from sendgrid.models import EmailMessageToData
from sendgrid.utils.cleanup import cleanup_email_message_body_data
from sendgrid.utils.cleanup import delete_email_message_body_data

ONE_DAY = datetime.timedelta(days=1)
ONE_WEEK = datetime.timedelta(weeks=1)


class Command(BaseCommand):
	help = "Prints a histogram of EmailMessageBodyData metadata"
	option_list = BaseCommand.option_list + (
		make_option("--resolution",
			default="days",
			type="string",
			help="Sets buckets size"
		),
	)

	def handle(self, *args, **kwargs):
		from sendgrid.histogram import DateBasedHistogram

		extraModels = (
			EmailMessageAttachmentsData,
			EmailMessageBodyData,
			EmailMessageBccData,
			EmailMessageCcData,
			EmailMessageExtraHeadersData,
			EmailMessageSendGridHeadersData,
			EmailMessageSubjectData,
			EmailMessageToData,
		)
		for model in (EmailMessage,) + extraModels:
			modelsObjectCount = model.objects.count()
			print("{modelId} ({count})".format(modelId=model._meta, count=modelsObjectCount))
			if model in extraModels:
				modelData = model.objects.values("email_message__creation_time").all()
				data = [item["email_message__creation_time"] for item in modelData]
			else:
				modelData = model.objects.values("creation_time").all()
				data = [item["creation_time"] for item in modelData]

			if modelsObjectCount == 0:
				print("\n")
				continue

			histData = DateBasedHistogram(data, "day").get_histogram_data()
			print("\t".join(["Key", "Count", "Freq"]))
			for k, v in histData.iteritems():
				rowItems = [k, len(v), len(v) / float(len(data))]
				strItems = map(str, rowItems)
				print("\t".join(strItems))
			print("\n")
