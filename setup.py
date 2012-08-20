#!/usr/bin/env python

from os import walk

from setuptools import setup, find_packages


# Automatically include all package data
with open('MANIFEST.in', 'w') as manifest:
    for dirpath, dirnames, filenames in walk('django_otp'):
        if (len(filenames) > 0) and ('__init__.py' not in filenames):
            manifest.write('recursive-include {0} *\n'.format(dirpath))
            dirnames[:] = []

    manifest.write('\nglobal-exclude .DS_Store *.pyc *.pyo .*.sw?\n')


setup(
    name='django-otp',
    version='0.1.0',
    description='A pluggable framework for adding two-factor authentication to Django using one-time passwords.',
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    url='https://bitbucket.org/psagers/django-otp',
    license='BSD',
    install_requires=[
        'django>=1.3'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 
