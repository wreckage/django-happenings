from __future__ import unicode_literals

from datetime import date

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
            'calendar:detail',
            kwargs={'pk': event.pk}
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
            'calendar:detail',
            kwargs={'pk': event.pk}
        ))
        self.assertContains(response, "The last event was on")


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
