"""The setup module for django_saml2_auth.
See:
https://github.com/fangli/django_saml2_auth
"""

from os import path

from setuptools import (setup, find_packages)

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='oauth2_sso',

    version='0.5.0',

    description='Django OAuth 2 Authentication Made Easy',

    url='https://github.com/saibot94/django-oauth2-sso',

    author='Cristian Schuszter',
    author_email='cristian.schuszter@cern.ch',

    license='MIT',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    install_requires=['requests>=2.0.0', 'Django>=1.6'],
    keywords=['Django', 'user', 'management', 'sign-up', 'user sync', 'authentication', 'authorization', 'OAuth',
              'SSO'],
    packages=find_packages(exclude=('tests*', '*tests', 'tests')),
    include_package_data=True,
    download_url='https://github.com/saibot94/django-oauth2-sso/archive/0.3.3.tar.gz'
)
