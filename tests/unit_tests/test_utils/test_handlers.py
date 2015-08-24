# This test file was created to fill in the untested portions of
# utils/handlers.py. Most of the tests for handlers.py are in integration_tests

from __future__ import unicode_literals

from collections import defaultdict
from datetime import date
from django.test.utils import override_settings

from happenings.utils import handlers as h
from tests.integration_tests.event_factory import create_event, SetMeUp


@override_settings(TIME_ZONE='UTC')
class TestHandlers(SetMeUp):
    """Tests the handlers for repeating events."""
    def setUp(self):
        self.counter = defaultdict(list)
        self.year = 2014
        self.month = 5

    def test_repeat_weekdays_day_out_of_range(self):
        """Should return unchanged dict."""
        day = 32
        end_repeat = None
        event = create_event(
            start_date=(2014, 5, 28),
            end_date=(2014, 5, 28),
            created_by=self.user,
            title="event",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        c = h.Repeater(
            self.counter, self.year, self.month, day, end_repeat, event
        ).repeat()
        self.assertEqual(len(c), 0)

    def test_repeat_weekdays_count_first_day(self):
        """Should return dict w/ first day counted."""
        day = 28
        end_repeat = date(2014, 7, 7)
        event = create_event(
            start_date=(2014, 5, 28),
            end_date=(2014, 5, 28),
            created_by=self.user,
            title="event",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        c = h.DailyRepeater(
            self.counter, self.year, self.month, day, end_repeat, event,
            count_first=True
        ).repeat_it()
        self.assertEqual(len(c), 3)
        self.assertEqual(c[28], [('event', event.pk)])
        self.assertEqual(c[29], [('event', event.pk)])
        self.assertEqual(c[30], [('event', event.pk)])

    def test_chunk_fill_out_first_week_stops_on_end_repeat(self):
        event = create_event(
            start_date=(2014, 4, 30),
            end_date=(2014, 5, 4),
            created_by=self.user,
            title="event",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2014, 5, 2),
            utc=True
        )
        c = h._chunk_fill_out_first_week(
            self.year, self.month, self.counter, event, event.get_start_end_diff()
        )
        self.assertEqual(len(c), 1)

    def test_repeat_reverse_out_of_range_start(self):
        """
        An out of range start day should not be counted, but any valid
        days that occur after the day has been decremented, should.
        """
        start = 33
        end = 30
        end_repeat = None
        event = create_event(
            start_date=(2014, 5, 28),
            end_date=(2014, 5, 28),
            created_by=self.user,
            title="event",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        c = h.Repeater(
            self.counter, self.year, self.month,
            end_repeat=end_repeat, event=event
        )
        c.repeat_reverse(start, end)
        self.assertEqual(len(c.count), 2)
        self.assertEqual(c.count[30], [('event', event.pk)])
        self.assertEqual(c.count[31], [('event', event.pk)])
