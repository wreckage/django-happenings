from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings

from happenings.models import Event


@override_settings(CALENDAR_SHOW_LIST=True)
class SetMeUp(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        html = '">%d</a><a class='
        cls.cal_str = lambda self, day: html % day
        cls.event_div = '<div class="calendar-event">'

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()


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
