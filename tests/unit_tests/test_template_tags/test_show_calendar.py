from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone

from happenings.models import Event
from happenings.templatetags.happenings_tags import show_calendar
from happenings.utils.common import now


class ShowCalendarTemplateTagTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('calendar:list')
        self.url_qs = reverse('calendar:list')

    def test_show_calendar_no_events(self):
        req = self.factory.get(self.url)
        cal = show_calendar({}, req)
        self.assertIn(str(now.month), cal)
        self.assertIn(str(now.year), cal)
        self.assertNotIn('calendar-event', cal)

    def test_mini_calendar(self):
        user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        event = Event.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now(),
            all_day=True,
            created_by=user,
            title="The big event",
            description="Amazing event",
            repeat="NEVER",
        )
        event2 = Event.objects.create(
            start_date=timezone.now() + timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            all_day=True,
            created_by=user,
            title="The other event",
            description="Incredible event",
            repeat="NEVER",
        )
        event.save()
        event2.save()

        req = self.factory.get(self.url, {'cal_category': 'birthday'})
        cal = show_calendar({}, req, mini=True)
        self.assertIn(str(now.month), cal)
        self.assertIn(str(now.year), cal)
        self.assertNotIn(event.title, cal)
        self.assertNotIn(event2.title, cal)
