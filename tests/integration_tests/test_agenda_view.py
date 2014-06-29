from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse

from .event_factory import create_event, SetMeUp


class AgendaViewTest(SetMeUp):
    def test_agenda_view_no_events(self):
        response = self.client.get(reverse('calendar:agenda'))
        self.assertContains(response, "No events")
        for i in range(3):
            self.assertEqual(0, len(response.context['events'][i]))

    def test_agenda_view_with_events(self):
        event1 = create_event(
            start_date=(2014, 2, 15),
            end_date=(2014, 2, 16),
            created_by=self.user,
            title="agenda event yay",
            description="This is it."
        )
        event2 = create_event(
            start_date=(2014, 3, 16),
            end_date=(2014, 3, 16),
            created_by=self.user,
            title="Another agenda event. yay.",
            description="This is also it."
        )
        response = self.client.get(reverse(
            'calendar:agenda_date', kwargs={'year': 2014, 'month': '2'}
        ))
        for d in ["February, 2014", "March, 2014", "April, 2014"]:
            self.assertContains(response, d)
        self.assertContains(response, event1.title)
        self.assertContains(response, event2.title)
        self.assertEqual(event1.title, response.context['events'][0][15][0][0])
        self.assertEqual(event1.title, response.context['events'][0][16][0][0])
        self.assertEqual(event2.title, response.context['events'][1][16][0][0])

    def test_agenda_view_with_cancelled_event(self):
        """
        Test that (CANCELLED) shows up next to the title of a
        cancelled event
        """
        event = create_event(
            start_date=(2014, 3, 20),
            end_date=(2014, 3, 20),
            created_by=self.user,
            title="agenda event yay",
            description="This is it."
        )
        c = event.cancellations.create(
            reason="Out of town",
            date=datetime.date(2014, 3, 20)
        )
        response = self.client.get(reverse(
            'calendar:agenda_date', kwargs={'year': 2014, 'month': '3'}
        ))
        self.assertContains(response, "(CANCELLED)")

    def test_agenda_view_months(self):
        """Test that the correct months are sent in the context."""
        response = self.client.get(reverse(
            'calendar:agenda_date', kwargs={'year': 2014, 'month': '2'}
        ))
        mos = [2, 3, 4, 5, 11]
        for i in range(5):
            year = 2014 if i < 4 else 2013
            self.assertEqual(year, response.context['months'][i].year)
            self.assertEqual(mos[i], response.context['months'][i].month)
