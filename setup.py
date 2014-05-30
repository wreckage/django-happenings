import os
from setuptools import setup, find_packages

import happenings

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-happenings',
    version=happenings.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A simple event calendar app for Django.',
    long_description=README,
    author='Reuben Urbina',
    author_email='reuben.urbina@gmail.com',
    url=happenings.__url__,
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'django >= 1.6, < 1.7',
        'pytz',
    ],
)
