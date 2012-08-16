import os
import sys
import time

import fabric
from fabric.api import *
from fabric.contrib.files import upload_template, exists
from fabric.operations import put, open_shell


PROJECT_ROOT = os.path.dirname(__file__)

REPOSITORY = "git@github.com:RyanBalfanz/django-sendgrid.git"
REPOSITORY_NAME = "django-sendgrid"

WEBFACTION_USERNAME = os.getenv("WEBFACTION_USER")
WEBFACTION_PASSWORD = os.getenv("WEBFACTION_PASSWORD")
WEBFACTION_HOST = os.getenv("WEBFACTION_HOST")
WEBFACTION_APPLICATION = os.getenv("WEBFACTION_APPLICATION")
WEBFACTION_APPLICATION_ROOT = "/home/{user}/webapps/{app}/".format(
	user=WEBFACTION_USERNAME,
	app=WEBFACTION_APPLICATION,
)
WEBFACTION_WEBSITE_URL = os.getenv("WEBFACTION_WEBSITE_URL")

if not WEBFACTION_HOST:
	WEBFACTION_HOST = "{username}.webfactional.com".format(username=WEBFACTION_USERNAME)

env.hosts = [WEBFACTION_HOST]
env.user = WEBFACTION_USERNAME
env.password = WEBFACTION_PASSWORD
env.home = "/home/{user}".format(user=WEBFACTION_USERNAME)
env.project = WEBFACTION_APPLICATION
env.repo = REPOSITORY
env.project_dir = env.home + "/webapps/" + WEBFACTION_APPLICATION
env.python_executable = "/usr/local/bin/python2.7"
env.SENDGRID_EMAIL_USERNAME = os.getenv("SENDGRID_EMAIL_USERNAME")
env.SENDGRID_EMAIL_PASSWORD = os.getenv("SENDGRID_EMAIL_PASSWORD")

WEBFACTION_DJANGO_PROJECT_ROOT = os.path.join(env.project_dir, "example_project")

@task
def release():
	fabric.operations.local("python setup.py sdist register upload")

@task
def pull():
	"""
	Runs git pull.
	"""
	with cd(os.path.join(env.project_dir, REPOSITORY_NAME)):
		run("git pull")

@task
def checkout(remote=None, branch="master"):
	"""
	Runs git checkout.
	"""
	with cd(os.path.join(env.project_dir, REPOSITORY_NAME)):
		if remote:
			checkoutCmd = "git checkout {remote} {branch}".format(remote=remote, branch=branch)
		else:
			checkoutCmd = "git checkout {branch}".format(branch=branch)

		run(checkoutCmd)

@task
def run_tests(surpress="output"):
	with hide(surpress):
		with cd(os.path.join(env.project_dir, REPOSITORY_NAME, "example_project")):
			run("{python} manage.py test".format(python=env.python_executable))

@task
def syncdb():
	"""
	Runs the migrations.
	"""
	with cd(os.path.join(env.project_dir, REPOSITORY_NAME, "example_project")):
		run("{python} manage.py syncdb".format(python=env.python_executable))

@task
def restart_apache():
	"""
	Restarts Apache.
	"""
	envVars = {
		"SENDGRID_EMAIL_USERNAME": env.SENDGRID_EMAIL_USERNAME,
		"SENDGRID_EMAIL_PASSWORD": env.SENDGRID_EMAIL_PASSWORD,
	}
	setEnv = ";".join("export {0}={1}".format(var, val) for var, val in envVars.iteritems())
	with prefix(setEnv):
		with cd(env.project_dir):
			run("./apache2/bin/restart")

@task
def get_memory_usage():
	run("ps -u {user} -o rss,command".format(user=WEBFACTION_USERNAME))

@task
def debug_on(filepath=None):
	if not filepath:
		filepath = "/home/{user}/webapps/djsendgrid/example_project/settings_local.py".format(user=WEBFACTION_USERNAME)
	cmd = "sed -i 's/False/True/' {file}".format(file=filepath)
	run(cmd)
	restart_apache()


@task
def debug_off(filepath=None):
	if not filepath:
		filepath = "/home/{user}/webapps/djsendgrid/example_project/settings_local.py".format(user=WEBFACTION_USERNAME)
	cmd = "sed -i 's/True/False/' {file}".format(file=filepath)
	run(cmd)
	restart_apache()

def put_files(files):
	"""
	Puts files on a remote host.
	"""
	for name, paths in files.iteritems():
		localPath, remotePath = paths["local"], paths["remote"]
		put(localPath, remotePath)

def get_url_open_time(url):
	import urllib2

	startTime = time.time()
	urllib2.urlopen(url)
	elapsedSeconds = time.time() - startTime

	return elapsedSeconds

def time_get_url(url, n=1):
	avg = lambda s: sum(s) / len(s)

	timings = []
	for i in range(n):
		timings.append(get_url_open_time(url))
		lastTiming = timings[-1]
		print("Retrieved in {s} seconds.".format(s=lastTiming))

	result = min(timings), avg(timings), max(timings)
	return result

@task
def update_settings():
	startTime = time.time()

	putFiles = {
		"settings_local.py": {
			"local": os.path.join(PROJECT_ROOT, "deploy/settings_local.py"),
			"remote": os.path.join(WEBFACTION_APPLICATION_ROOT, "example_project", "settings_local.py")
		},
	}
	put_files(putFiles)
	restart_apache()
	elapsedSeconds = time.time() - startTime
	print("Updated in {s} seconds!".format(s=elapsedSeconds))

	print time_get_url(WEBFACTION_WEBSITE_URL, n=3)

@task
def deploy(branch):
	"""
	Deploys the application.
	"""
	startTime = time.time()

	putFiles = {
		"settings_local.py": {
			"local": os.path.join(PROJECT_ROOT, "deploy/settings_local.py"),
			"remote": os.path.join(WEBFACTION_APPLICATION_ROOT, "example_project", "settings_local.py")
		},
		"example_project.wsgi": {
			"local": os.path.join(PROJECT_ROOT, "deploy/example_project.wsgi"),
			"remote": os.path.join(WEBFACTION_APPLICATION_ROOT, "example_project.wsgi")
		},
		"httpd.conf": {
			"local": os.path.join(PROJECT_ROOT, "deploy/apache2/conf/httpd.conf"),
			"remote": os.path.join(WEBFACTION_APPLICATION_ROOT, "apache2/conf/httpd.conf")
		},
	}
	put_files(putFiles)

	pull()
	checkout(branch=branch)
	# run_tests()
	# syncdb()
	restart_apache()

	elapsedSeconds = time.time() - startTime
	print("Deployed in {s} seconds!".format(s=elapsedSeconds))

	print time_get_url(WEBFACTION_WEBSITE_URL, n=3)

def watch_logs(prefix="access", n=10, follow=False):
	"""docstring for watch_logs"""

	logPathOverrides = {
		"django": os.path.join(WEBFACTION_DJANGO_PROJECT_ROOT, "example_project.log"),
	}
	with cd(env.home):
		if prefix in logPathOverrides:
			logFile = logPathOverrides[prefix]
		else:
			logFile = os.path.join(env.home, "logs", "user", "{prefix}_{app}.log").format(prefix=prefix, app=WEBFACTION_APPLICATION)

		if follow:
			cmd = "tail -n {n} -f {file}".format(n=n, file=logFile)
		else:
			cmd = "tail -n {n} {file}".format(n=n, file=logFile)

		run(cmd)

@task
def access_logs(n=10, follow=True):
	watch_logs("access", n, follow)

@task
def error_logs(n=10, follow=True):
	watch_logs("error", n, follow)

def django_logs(n=10, follow=True):
	watch_logs("django", n, follow)

@task
def logs(logType="access"):
	"""
	Tails the logs.
	"""
	startTime = time.time()

	delegates = {
		"access": access_logs,
		"error": error_logs,
		"django": django_logs,
	}
	try:
		f = delegates[logType]
	except KeyError:
		raise ValueError("Unrecognized log type '{}'".format(logType))
	else:
		f()
		# f(n, follow)
	finally:
		elapsedSeconds = time.time() - startTime
		print "Elapsed time (s): {n}".format(n=elapsedSeconds)

@task
def shell(*args, **kwargs):
	envVars = {
		"SENDGRID_EMAIL_USERNAME": env.SENDGRID_EMAIL_USERNAME,
		"SENDGRID_EMAIL_PASSWORD": env.SENDGRID_EMAIL_PASSWORD,
		# "PYTHONPATH:": env.python_executable + ":$PYTHONPATH",
	}
	setEnv = ";".join("export {0}={1}".format(var, val) for var, val in envVars.iteritems())
	with prefix(setEnv):
		open_shell(*args, **kwargs)
