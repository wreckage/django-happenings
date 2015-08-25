from __future__ import unicode_literals

from datetime import date
from collections import defaultdict

from tests.integration_tests.event_factory import create_event, SetMeUp
from happenings.utils.calendars import EventCalendar, MiniEventCalendar


class EventCalendarTest(SetMeUp):
    def test_location(self):
        """
        Test that, if an event has a location associated with it, it gets
        set when popover_helper() is called (the event location only appears
        in the popover on the month calendar view page).
        """
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
        # Test first without a location
        events = [event]
        day = 15
        count_dict = {day: [(event.title, event.pk)]}

        cal = EventCalendar(yr, mo, count, events)
        cal.count = count_dict
        render_result = cal.formatday(day, 0)
        self.assertNotIn("Where:", render_result)
        self.assertNotIn("Heck", render_result)

        # Test with a location
        event.location.create(
            name="Heck"
        )
        events = [event]
        cal2 = EventCalendar(yr, mo, count, events)
        cal2.count = count_dict
        render_result = cal2.formatday(day, 0)
        self.assertIn("Where:", render_result)
        self.assertIn("Heck", render_result)


class MiniEventCalendarTest(SetMeUp):
    def test_popover_helper(self):
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
        days = (15, 22, 29)
        [count[day].append((event.title, event.pk)) for day in days]
        events = [event]
        cal = MiniEventCalendar(yr, mo, count, events)
        cal.event = event
        for day in days:
            cal.title = event.title
            cal.day = day
            cal.count = {day: [(event.title, event.pk)]}
            rendered_result = cal.formatday(day, 0)
            self.assertIn(event.title, rendered_result)
