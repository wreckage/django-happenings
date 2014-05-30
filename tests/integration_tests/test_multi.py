from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from .event_factory import create_event, SetMeUp


class MultipleEventsListViewTest(SetMeUp):
    """
    There's already a test called test_list_view_with_multiple_events
    in test_month_view, but this takes it a step further.
    Created in response to discovering a bug related to repeat_biweekly
    in handlers.py after moving from functions to classes. Noticed that
    it was clearing the counter used to keep track of all events,
    but no tests caught the problem.
    """
    def test_multi(self):
        event1 = create_event(
            start_date=(2014, 5, 28),
            end_date=(2014, 5, 28),
            created_by=self.user,
            title="Whoa",
            description="Ehhh",
            repeat="BIWEEKLY",
        )
        event2 = create_event(
            start_date=(2014, 5, 28),
            end_date=(2014, 5, 28),
            created_by=self.user,
            title="The Coolest",
            description="Cool event dude!",
            repeat="WEEKDAY",
        )

        event3 = create_event(
            start_date=(2014, 5, 26),
            end_date=(2014, 5, 26),
            created_by=self.user,
            title="QWERTY",
            description="ASDFGH",
            repeat="WEEKLY",
        )

        events = {
            event1.title: event1.description,
            event2.title: event2.description,
            event3.title: event3.description,
        }
        for month in ('5', '6'):
            response = self.client.get(reverse(
                'calendar:list', kwargs={'year': '2014', 'month': month}
            ))
            for k, v in events.items():
                self.assertContains(response, k)
                self.assertContains(response, v)
