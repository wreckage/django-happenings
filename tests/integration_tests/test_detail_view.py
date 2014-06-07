from __future__ import unicode_literals

import re
from datetime import date, timedelta

from django.utils import timezone
from django.core.urlresolvers import reverse

from .event_factory import create_event, SetMeUp


class EventDetailViewTest(SetMeUp):

    def test_detail_view_with_no_events(self):
        """Going to a url for an event that doesn't exist should return 404."""
        response = self.client.get(reverse(
            'calendar:detail',
            kwargs={'pk': 1}
        ))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_event(self):
        """
        Going to a url for an event that exists should display the event's
        details.
        """
        event = create_event(
            start_date=(2015, 2, 15),
            end_date=(2015, 2, 16),
            created_by=self.user,
            title="The Event",
            description="This is an event for next month.",
            full=False
        )
        response = self.client.get(reverse(
            'calendar:detail',
            kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "This is an event")

    def test_detail_view_with_repeating_event(self):
        event = create_event(
            start_date=(2014, 2, 15),
            end_date=(2014, 2, 16),
            created_by=self.user,
            title="The Event",
            description="This is an event that is still repeating.",
            repeat='MONTHLY',
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "This event repeats")

    def test_detail_view_with_repeating_event_that_is_done_repeating(self):
        event = create_event(
            start_date=(2012, 2, 15),
            end_date=(2012, 2, 15),
            created_by=self.user,
            title="The Event",
            description="This is an event that has finished repeating.",
            repeat='WEEKDAY',
            end_repeat=date(2012, 5, 15)
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "The last event was on")

    def test_detail_view_with_cancelled_single_day_event(self):
        event = create_event(
            start_date=(2014, 5, 15),
            end_date=(2014, 5, 15),
            created_by=self.user,
            title="The Event",
            description="This event has been cancelled.",
        )
        event.cancellations.create(
            reason="Out sick", date=date(2014, 5, 15)
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "CANCELLED")

    def test_detail_view_with_cancelled_non_repeating_chunk_event(self):
        event = create_event(
            start_date=(2014, 5, 15),
            end_date=(2014, 5, 17),
            created_by=self.user,
            title="The Event",
            description="Cancelled? Maybe.",
        )
        event.cancellations.create(
            reason="Out sick", date=date(2014, 5, 16)
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "Day 1: Thu May 15, 2014")
        self.assertContains(response, "Day 2: Fri May 16, 2014")
        self.assertContains(response, "Day 3: Sat May 17, 2014")
        match = re.findall("CANCELLED", str(response.content))
        self.assertEqual(1, len(match))

    def test_detail_view_with_next_cancelled_single_day_event(self):
        """Test that CANCELLED shows up if next event is cancelled."""
        d1 = timezone.localtime(timezone.now() - timedelta(days=3))
        event = create_event(
            start_date=(d1.year, d1.month, d1.day),
            end_date=(d1.year, d1.month, d1.day),
            created_by=self.user,
            title="The Event",
            description="Blah",
            repeat="WEEKLY",
        )
        d2 = timezone.localtime(timezone.now() + timedelta(days=4))
        event.cancellations.create(
            reason="Out sick", date=d2
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "Next event")
        self.assertContains(response, "CANCELLED")

    def test_detail_view_with_cancelled_event_in_past(self):
        """Events that were cancelled in the past shouldn't show, but events
        in the future should."""
        event = create_event(
            start_date=(2014, 4, 15),
            end_date=(2014, 4, 15),
            created_by=self.user,
            title="The Event",
            description="doom",
            repeat="MONTHLY"
        )
        event.cancellations.create(
            reason="Out sick", date=date(2025, 5, 15)
        )
        event.cancellations.create(
            reason="Surfing", date=date(2014, 5, 15)
        )
        response = self.client.get(reverse(
            'calendar:detail', kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "Thu May 15, 2025")
        self.assertNotContains(response, "Thu May 15, 2014")


class EventListViewTagTest(SetMeUp):
    def test_list_view_event_with_tag(self):
        event = create_event(
            created_by=self.user,
            title="Auron",
            description="Just an event.",
            tags=["foo"]
        )
        event2 = create_event(
            created_by=self.user,
            title="Jen",
            description="Another one"
        )

        response = self.client.get(
            reverse('calendar:list'), {'cal_tag': 'foo'}
        )
        self.assertContains(response, event.title)
        self.assertNotContains(response, event2.title)
        self.assertContains(response, 'class="calendar-event"')
