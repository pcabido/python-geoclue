#! /usr/bin/env python

import sys,os
sys.path.insert(0,os.getcwd())
import Geoclue

from distutils.core import setup

VERSION = '0.1.0'
setup(name='python-geoclue',
        version=VERSION, 
        author='Paulo Cabido',
        author_email='paulo.cabido@gmail.com',
        url='http://were.it.is.hosted',
#        download_url='http://were.it.is.hosted/files/python-geoclue-%s.tar.gz' % VERSION,
        description='Geoclue python module',
        license='GLP3',
        long_description="""
        Python-Geoclue is nice API interface for Geoclue.
        Almost all Geoclue methods are available.
        
        It uses the Geoclue D-Bus API in order to facilitate Geoclue's use.
        """,
        packages=['Geoclue'],
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
#        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
        )
