#!/usr/bin/env python
import os
import sys
import codecs

try:
	from setuptools import setup, find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

import sendgrid as distmeta

packages = find_packages(exclude=("example_project",))
data_files = []
root_dir = os.path.dirname(__file__)

if root_dir != '':
	os.chdir(root_dir)
src_dir = "sendgrid"

if os.path.exists("README.rst"):
	long_description = codecs.open("README.rst", "r", "utf-8").read()
else:
	long_description = "See http://ryanbalfanz.github.com/django-sendgrid/"

setup(
	name='django-sendgrid',
	version=distmeta.__version__,
	description=distmeta.__doc__,
	author=distmeta.__author__,
	author_email=distmeta.__contact__,
	url=distmeta.__homepage__,
	platforms=["any"],
	# license="BSD",
	packages=packages,
	package_dir={'sendgrid': 'sendgrid'},
	package_data={'sendgrid': ['fixtures/initial_data.json']},
	data_files=data_files,
	long_description=long_description,
	install_requires=[
		'django>=1.3.1',
		'South>=0.7.5',
	],
)
