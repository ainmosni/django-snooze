#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import django_snooze

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = django_snooze.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-snooze',
    version=version,
    description="""A fast, easy REST framework for Django, intended to replace external database access.""",
    long_description=readme + '\n\n' + history,
    author='Daniël Franke',
    author_email='daniel@ams-sec.org',
    url='https://github.com/ainmosni/django-snooze',
    packages=[
        'django_snooze',
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.3',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-snooze',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
