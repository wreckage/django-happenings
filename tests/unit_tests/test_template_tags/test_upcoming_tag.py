from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.timezone import make_aware, get_default_timezone

from happenings.models import Event
from happenings.templatetags.happenings_tags import upcoming_events


class UpcomingEventsTemplateTagTest(TestCase):
    """
    Test that upcoming_events template tag returns upcoming_events.
    For more thorough tests see integration_tests.test_upcoming_events.
    """

    def setUp(self):
        self.url = reverse('calendar:list')

    def test_upcoming_events_no_events(self):
        events = upcoming_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events['upcoming_events'], [])

    def test_events_same_date(self):
        """Created June 13, 2014 after a bug was found."""
        user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        d = make_aware(
            datetime.datetime(2019, 5, 3, 0, 0, 0, 0),
            get_default_timezone()
        )
        event = Event.objects.create(
            start_date=d,
            end_date=d,
            all_day=True,
            created_by=user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
        )
        event2 = Event.objects.create(
            start_date=d,
            end_date=d,
            all_day=True,
            created_by=user,
            title="The other event",
            description="Incredible event",
            repeat="NEVER",
        )
        event.save()
        event2.save()
        events = upcoming_events(finish=2000)
        self.assertEqual(len(events['upcoming_events']), 2)
