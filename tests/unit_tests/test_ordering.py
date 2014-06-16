from __future__ import unicode_literals

import datetime

from django.utils.timezone import make_aware, get_default_timezone
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.test import TestCase
from django.contrib.auth.models import User

from happenings.models import Event


class EventOrderingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        d0 = make_aware(
            datetime.datetime(2014, 5, 20, 4), get_default_timezone()
        )
        d1 = make_aware(
            datetime.datetime(2014, 5, 20, 5), get_default_timezone()
        )
        d2 = make_aware(
            datetime.datetime(2014, 5, 20, 6), get_default_timezone()
        )
        d3 = make_aware(
            datetime.datetime(2014, 5, 20, 7), get_default_timezone()
        )
        self.event1 = Event.objects.create(
            start_date=d1,
            end_date=d2,
            all_day=True,
            created_by=self.user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
        )
        self.event2 = Event.objects.create(
            start_date=d2,
            end_date=d3,
            all_day=True,
            created_by=self.user,
            title="The next big event",
            description="Amazing next event",
            repeat="NEVER",
        )
        self.event3 = Event.objects.create(
            start_date=d0,
            end_date=d1,
            all_day=True,
            created_by=self.user,
            title="uhh event",
            description="Cool",
            repeat="NEVER",
        )

    def assertContentBefore(self, response, text1, text2):
        """
        Testing utility asserting that text1 appears before text2 in response
        content. Modified from:
        https://github.com/django/django/blob/master/tests/admin_views/tests.py
        """
        failing_msg = "%s not found before %s" % (text1, text2)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.content.index(force_bytes(text1)) <
            response.content.index(force_bytes(text2)),
            failing_msg)

    def test_ordering_month_view(self):
        response = self.client.get(reverse(
            'calendar:list', kwargs={'year': '2014', 'month': '5'}
        ))
        self.assertContentBefore(
            response, self.event3.title, self.event1.title
        )
        self.assertContentBefore(
            response, self.event1.title, self.event2.title
        )

    def test_ordering_day_view(self):
        response = self.client.get(reverse(
            'calendar:day_list',
            kwargs={'year': '2014', 'month': '5', 'day': '20'}
        ))
        self.assertContentBefore(
            response, self.event3.title, self.event1.title
        )
        self.assertContentBefore(
            response, self.event1.title, self.event2.title
        )
