=================
Django Happenings
=================

|travis| |coverage| |version|

An event calendar app for Django.

Features:

* Repeating and non-repeating events
* Events that start and end on different days
* Upcoming events list
* AJAX support
* Default CSS & Javascript to help you get started

Coming soon:

* better integration of categories and tags
* more views, including an agenda view
* support for users
* support for cancelled events
* ++ more


Dependencies
------------

Required:

* Django 1.6+
* Python 2.6+, 3+
* pytz

Optional:

* jQuery
* Twitter Bootstrap 3.0.0+ (w/ tooltip plugin)
* South (for database migrations)

jQuery is used for AJAX and the 'Today' button on the calendar.

TWBS is used to create popovers when an event is clicked on the calendar.

Quick Install
-------------

1. Install with ``pip``::

   $ pip install django-happenings

2. Add ``happenings`` to ``INSTALLED_APPS``:

.. code-block:: python

  INSTALLED_APPS = (
    ...
    'happenings'
  )

3. Include the ``django-happenings`` URLconf in urls.py:

.. code-block:: python

  url(r'^calendar/', include('happenings.urls', namespace='calendar'))

4. Make sure your ``TIME_ZONE`` is set correctly in settings.py.

5. Run ``python manage.py syncdb`` to create the models (replace ``syncdb`` with 
   ``migrate happenings`` if using South). If you're running MySQL, be sure that
   your database is properly configured to use time zones.

6. Run the development server and go to ``127.0.0.1:8000/admin/`` to create and manage events.

7. Check out the calendar at ``127.0.0.1:8000/calendar/``.

Customizing
-------------

The quickest way to begin customizing the app is to override the
``middle.html`` template by creating your own version in 
<mytemplates>/happenings/middle.html (replace <mytemplates> with wherever
you keep your templates) and add the line ``{% extends 'base.html' %}``
(replace base.html with your base template). For a greater degree of customization,
you can copy and paste into your project all of the templates included in the app, and
change them to fit your needs.

Be sure to include the packaged css & javascript into your base template if you
want to use them. Loading the default style into your template would 
look something like (assuming staticfiles has been loaded)::

    <link href=" {% static 'happenings/css/calendar.css' %}" rel="stylesheet">

And the default javascript something like::

    <script src="{% static 'happenings/js/calendar.js' %}"></script>

Template Tags
-------------

Template tags are available by loading ``happenings_tags`` into your template::

    {% load happenings_tags %}

This gives access to two template tags: ``show_calendar`` and ``upcoming_events``.

Use ``show_calendar`` like this::

    <div id="event-calendar">
        {% show_calendar request %}
    </div>

to display a calendar like the one in ``/calendar/``, or like this::

    <div id="event-calendar" class="calendar-mini">
        {% show_calendar request mini=True %}
    </div>

to display a mini calendar. The ``<div>`` shown allows you to use the styles
included with the app, but you can omit or change them if you want to use 
your own style. Note also that the request object needs to be included in the tag.

Include ``upcoming_events`` in your template like this::

    {% upcoming_events %}

to display a list of the next 5 (or less) upcoming events within the next 90 days.
If you'd like to show events that occur outside of 90 days, or show more events in the
list, use the ``finish`` and ``num`` options::

    {% upcoming_events finish=365 num=8 %}
    
Optional Settings
-------------

You can specify different settings for the app in your settings.py file.

Use ``CALENDAR_COLORS`` to add a custom color to the drop down in the admin when
creating an event. Example of setting the custom color 'fuchsia'::

    CALENDAR_COLORS = [('ff00ff', 'fuchsia')]

Use ``CALENDAR_START_DAY`` to change the day on which the calendar starts. Example
of starting the calendar on Sunday (instead of the default of Monday)::

    CALENDAR_START_DAY = 6

There are no translations from English yet, but if you'd like to display the calendar
and the event list in a different language, you can use ``CALENDAR_LOCALE``. The upcoming
events list won't be translated, though. For that you'll need to specify your ``LANGUAGE_CODE``
in the Django settings. Also note that to use ``CALENDAR_LOCALE`` you'll need to have the correct
locale pack installed for your system. Example of changing the language to German::

    CALENDAR_LOCALE = 'de_DE.utf8'

Tests
-------------

``Tox`` is used for testing.

``$ pip install tox``

``$ tox -e py27-django16``

More To Come!
-------------

.. |travis| image:: https://travis-ci.org/wreckage/django-happenings.svg?branch=master
   :alt: Build Status - master branch
   :target: https://travis-ci.org/wreckage/django-happenings
.. |coverage| image:: https://coveralls.io/repos/wreckage/django-happenings/badge.png?branch=master
   :alt: Coverage Status
   :target: https://coveralls.io/r/wreckage/django-happenings?branch=master
.. |version| image:: https://badge.fury.io/py/django-happenings.svg
   :alt: Pypi Version
   :target: https://badge.fury.io/py/django-happenings
