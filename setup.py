# -*- coding: utf-8 -
#
# This file is part of django-template-speedup released under the MIT license. 
# See the LICENSE for more information.

import os
from setuptools import setup, find_packages

setup(
    name='django-template-speedup',
    version=__import__('template_speedup').VERSION,
    description='Some speedup for django template system',
    long_description=open('README.md').read(),
    author='Victor Safronovich',
    author_email='vsafronovich@gmail.com',
    license='MIT',
    url='https://github.com/suvit/django-template-speedup',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    #install_requires=['django'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Web Environment',
        'Topic :: Software Development',
    ]
)
