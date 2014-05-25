from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

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
