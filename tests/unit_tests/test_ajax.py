from __future__ import unicode_literals

from json import loads

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.test.utils import override_settings

from happenings.models import Event


@override_settings(CALENDAR_SHOW_LIST=True)
class AjaxTest(TestCase):
    """Test that urls expecting ajax return appropriate data."""
    def test_ajax_month_calendar(self):
        response = self.client.get(
            reverse('calendar:month_shift'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response['Content-Type'], 'application/json')

        data = loads(response.content.decode('utf8'))
        self.assertIn('<table', data['calendar'])
        self.assertIn('month_and_year', data)

    def test_ajax_event_list(self):
        user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        Event.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now(),
            all_day=True,
            created_by=user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
        )
        response = self.client.get(
            reverse('calendar:event_list_shift'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response['Content-Type'], 'application/json')

        data = loads(response.content.decode('utf8'))
        self.assertIn('events', data)
        self.assertIn('month', data)

    def test_ajax_month_calendar_and_event_list(self):
        """Test getting both the calendar and event list via ajax."""
        response = self.client.get(
            reverse('calendar:cal_and_list_shift'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response['Content-Type'], 'application/json')

        data = loads(response.content.decode('utf8'))
        self.assertEqual({}, data['events'])
        self.assertIn('month', data)
        self.assertIn('<table', data['calendar'])
        self.assertIn('month_and_year', data)

    def test_ajax_day_view(self):
        """Test sending an ajax request to day view."""
        response = self.client.get(
            reverse(
                'calendar:day_list',
                kwargs={'year': '2015', 'month': '2', 'day': '2'}
            ),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response['Content-Type'], 'application/json')

        data = loads(response.content.decode('utf8'))
        self.assertEqual([], data['events'])
