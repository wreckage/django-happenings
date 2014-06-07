from __future__ import unicode_literals

from datetime import date
from collections import defaultdict

from tests.integration_tests.event_factory import create_event, SetMeUp
from happenings.utils.calendars import GenericCalendar


class CancelledEventsTest(SetMeUp):
    def test_cancelled_single_day_event(self):
        yr = 2014
        mo = 5
        count = defaultdict(list)
        event = create_event(
            start_date=(2014, 5, 15),
            end_date=(2014, 5, 15),
            created_by=self.user,
            title="Big Event",
            description="Wow! An event.",
            repeat="WEEKLY"
        )
        event.cancellations.create(
            reason="Out of town",
            date=date(2014, 5, 22)
        )
        days = (15, 22, 29)
        [count[day].append((event.title, event.pk)) for day in days]
        events = [event]
        cal = GenericCalendar(yr, mo, count, events)
        cal.event = event
        for day in days:
            cal.title = event.title
            cal.day = day
            cal.check_if_cancelled()
            if day == 22:
                self.assertEqual(event.title + ' (CANCELLED)', cal.title)
            else:
                self.assertEqual(event.title, cal.title)

    def test_cancelled_chunk_event(self):
        """Only the date given in the cancellation should show up cancelled.
        This means that a two day event with only the first day cancelled,
        should only show (CANCELLED) for the first day."""
        yr = 2014
        mo = 5
        count = defaultdict(list)
        event = create_event(
            start_date=(2014, 5, 15),
            end_date=(2014, 5, 16),
            created_by=self.user,
            title="Big Event",
            description="Wow! An event.",
            repeat="WEEKLY"
        )
        event.cancellations.create(
            reason="Out of town",
            date=date(2014, 5, 22)
        )
        days = (15, 16, 22, 23, 29, 30)
        [count[day].append((event.title, event.pk)) for day in days]
        events = [event]
        cal = GenericCalendar(yr, mo, count, events)
        cal.event = event
        for day in days:
            cal.title = event.title
            cal.day = day
            cal.check_if_cancelled()
            if day == 22:
                self.assertEqual(event.title + ' (CANCELLED)', cal.title)
            else:
                self.assertEqual(event.title, cal.title)
