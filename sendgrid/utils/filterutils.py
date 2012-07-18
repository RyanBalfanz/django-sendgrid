from django.conf import settings


PASS = lambda i: True
FAIL = lambda i: False
IS_ZERO_OR_ONE = lambda i: i in (0, 1, "0", "1")

INTERFACES = {
	"gravatar": ["enable"],
	"clicktrack": ["enable"],
	"subscriptiontrack": ["enable", "text/html", "text/plain", "replace", "url", "landing"],
	"opentrack": ["enable"],
}

FILTER_SETTING_VALUE_TESTS = {
	"gravatar.enable": IS_ZERO_OR_ONE,
	"clicktrack.enable": IS_ZERO_OR_ONE,
	"subscriptiontrack.enable": IS_ZERO_OR_ONE,
	"subscriptiontrack.text/html": PASS,
	"opentrack.enable": IS_ZERO_OR_ONE,
}

IGNORE_MISSING_TESTS = getattr(settings, "IGNORE_MISSING_TESTS", False)
VALIDATE_FILTER_SPECIFICATION = getattr(settings, "VALIDATE_FILTER_SPECIFICATION", True)

def validate_filter_setting_value(filter, setting, value, ignoreMissingTests=IGNORE_MISSING_TESTS):
	"""
	Validates the given value for the filter setting.
	"""
	if filter not in INTERFACES:
		raise AttributeError("The filter {f} is not valid".format(f=filter))
		
	if setting not in INTERFACES[filter]:
		raise AttributeError("The setting {s} is not valid for the filter {f}".format(s=setting, f=filter))
		
	testName = ".".join([filter, setting])
	try:
		test = FILTER_SETTING_VALUE_TESTS[testName]
	except KeyError as e:
		if ignoreMissingTests:
			result = True
		else:
			raise e
	else:
		result = test(value)
		
	return result

def validate_filter_specification(f):
	"""
	Validates a given filter specification.
	"""
	passedAllTests = None

	testResults = {}
	for filter, spec in f.iteritems():
		for setting, value in spec.iteritems():
			testKey = ".".join([filter, setting])
			testResult = validate_filter_setting_value(filter, setting, value)
			testResults[testKey] = testResult

	resultSet = set(testResults.values())
	passedAllTests = len(resultSet) == 1 and True in resultSet
	return passedAllTests

def update_filters(email, filterSpec, validate=VALIDATE_FILTER_SPECIFICATION):
	"""
	Updates the ``SendGridEmailMessage`` filters, optionally validating the given sepcification.
	"""
	if validate:
		filterSpecIsValid = validate_filter_specification(filterSpec)
		if not filterSpecIsValid:
			raise Exception("Invalid filter specification")
			
	for filter, spec in filterSpec.iteritems():
		for setting, value in spec.iteritems():
			email.sendgrid_headers.addFilterSetting(fltr=filter, setting=setting, val=value)

	return
