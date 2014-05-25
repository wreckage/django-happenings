from __future__ import unicode_literals

from datetime import datetime, date

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import make_aware, utc

from happenings.models import Event
from tests.integration_tests.event_factory import create_event


class EventManagerTest(TestCase):
    def test_live(self):
        """Tests that Event.objects.live() returns events that could occur."""
        user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        event = create_event(
            start_date=(2014, 5, 1),
            end_date=(2014, 5, 1),
            created_by=user,
            title="kowabunga",
            description="Testing 1 2 3",
            repeat="BIWEEKLY",
            utc=True
        )
        event2 = create_event(
            start_date=(2014, 6, 1),
            end_date=(2014, 6, 1),
            created_by=user,
            title="kowabunga",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        event3 = create_event(
            start_date=(2014, 5, 2),
            end_date=(2014, 5, 4),
            created_by=user,
            title="gnarly",
            description="Testing 1 2 3",
            repeat="NEVER",
            utc=True
        )
        event4 = create_event(
            start_date=(2014, 4, 2),
            end_date=(2014, 4, 4),
            created_by=user,
            title="tubular",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2014, 5, 2),
            utc=True
        )
        event.save()
        event2.save()
        event3.save()
        event4.save()
        now = make_aware(datetime(2014, 5, 6), utc)
        events = Event.objects.live(now)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].title, event.title)
        self.assertEqual(events[0].pk, event.pk)
        self.assertEqual(events[1].title, event2.title)
        self.assertEqual(events[1].pk, event2.pk)
