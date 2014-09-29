import collections
import datetime
import itertools
import random
import time


def random_datetime(start, end):
	"""
	Returns a random datetime object in the given range.
	"""
	startSecs = time.mktime(start.timetuple())
	endSecs = time.mktime(end.timetuple())
	timeRange = endSecs - startSecs

	rand = random.random()
	randSecs = (endSecs - startSecs)*rand + startSecs

	return datetime.datetime.fromtimestamp(randSecs)


class DateBasedHistogram(object):
	"""
	Transforms datetime-based data into a histogram.
	"""
	def __init__(self, data, resolution=None):
		self.data = data
		if not resolution:
			resolution = "month"

		assert resolution in ("day", "month", "year")
		self.resolution = resolution

	def get_histogram_data(self):
		grouperMap = {
			"day": lambda x: '%s.%s.%s' % (x.year, x.month, x.day),
			"month": lambda x: '%s.%s' % (x.year, x.month),
			"year": lambda x: '%s' % (x.year,)
		}
		grouper = grouperMap[self.resolution]

		histoData = collections.defaultdict(list)
		for key, group in itertools.groupby(self.data, key=grouper):
			for item in group:
				histoData[key].append(item)

		return histoData


if __name__ == "__main__":
	today = datetime.datetime.now().date()
	oneDay = datetime.timedelta(days=1)
	start, end = today - 60*oneDay, today
	randDatetimes = [random_datetime(start, end) for i in range(1000)]

	dbh = DateBasedHistogram(randDatetimes, resolution="month")
	for k, v in dbh.get_histogram_data().iteritems():
		print k, len(v), len(v) / float(len(randDatetimes))
