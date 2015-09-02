# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings

import six

from happenings.models import Event


@override_settings(CALENDAR_SHOW_LIST=True)
class SetMeUp(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SetMeUp, cls).setUpClass()
        cls.user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        html = '">%d</a><a class='
        cls.cal_str = lambda self, day: html % day
        cls.event_div = '<div class="calendar-event">'

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def clean_whitespace(self, response):
        """Remove all newlines and all occurances of multiple spaces."""
        if hasattr(response, 'content'):
            is_response = True
            content = response.content
        else:
            is_response = False
            content = response

        if isinstance(content, six.text_type):
            content = content.encode('utf-8')

        content = content.replace(b'\n', b'')

        for num_spaces in range(7, 2, -1):
            # reduce all multiple spaces to 2 spaces.
            # We can process here only `num_spaces=3` with the same result, but it will be slower
            while content.find(b' '*num_spaces) >= 0:
                content = content.replace(b' '*num_spaces, b' '*2)
        content = content.replace(b' '*2, b'')
        if is_response:
            response.content = content
        else:
            content = content.decode('utf-8')
        return content

def create_event(created_by, title, description, all_day=False,
                 start_date=None, end_date=None, categories=None, tags=None,
                 repeat='NEVER', end_repeat=None, full=True, utc=False):
    """
    A factory method for creating events. If start_date is supplied,
    end_date must also be supplied, and they must both be either lists
    or tuples e.g. start_date=[2014, 2, 2], end_date=[2014, 2, 3].
    """
    if start_date and end_date:
        # Set the start and end dates to local tz
        if utc:
            val = timezone.utc
        else:
            val = timezone.get_default_timezone()
        start_date = timezone.make_aware(datetime.datetime(*start_date), val)
        end_date = timezone.make_aware(datetime.datetime(*end_date), val)

    elif start_date and not end_date or end_date and not start_date:
        raise ValueError("Both start_date and end_date must be supplied or not"
                         " supplied at all when using create_event")
    else:
        start_date = timezone.now()
        end_date = timezone.now()
    event = Event.objects.create(
        start_date=start_date,
        end_date=end_date,
        all_day=all_day,
        created_by=created_by,
        title=title,
        description=description,
        repeat=repeat,
        end_repeat=end_repeat
    )

    if categories:
        for category in categories:
            event.categories.create(title=category)

    if tags:
        for tag in tags:
            event.tags.create(name=tag)

    if full:
        event.full_clean()
        event.save()
    return event
