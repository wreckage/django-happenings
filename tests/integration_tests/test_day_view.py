from __future__ import unicode_literals

from datetime import date

from django.core.urlresolvers import reverse

from .event_factory import create_event, SetMeUp


class EventDayListViewDisplayTest(SetMeUp):
    def test_list_view_year_and_month_and_day_in_url(self):
        """
        Test that an event shows up if a year & month & day are entered
        into the url, and the event is scheduled to occur on that day.
        """
        event1 = create_event(
            start_date=(2015, 2, 15),
            end_date=(2015, 2, 16),
            created_by=self.user,
            title="Bailey",
            description="This is an event for next month."
        )
        event2 = create_event(
            start_date=(2015, 2, 15),
            end_date=(2015, 2, 16),
            created_by=self.user,
            title="Natalia",
            description="This is an event for next month."
        )
        event3 = create_event(
            start_date=(2015, 2, 20),
            end_date=(2015, 2, 23),
            created_by=self.user,
            title="Judith",
            description="This is an event for next month."
        )

        for day in range(15, 17):
            response = self.client.get(reverse(
                'calendar:day_list',
                kwargs={'year': '2015', 'month': '2', 'day': day}
            ))
            self.assertContains(response, event1.title)
            self.assertContains(response, event2.title)
            self.assertNotContains(response, event3.title)

            response = self.client.get(reverse(
                'calendar:day_list',
                kwargs={'year': '2016', 'month': '2', 'day': day}
            ))
            self.assertContains(response, "No events")

        for day in range(20, 24):
            response = self.client.get(reverse(
                'calendar:day_list',
                kwargs={'year': '2015', 'month': '2', 'day': day}
            ))
            self.assertNotContains(response, event1.title)
            self.assertNotContains(response, event2.title)
            self.assertContains(response, event3.title)

    def test_list_view_year_and_month_and_day_in_url_repeating_chunk(self):
        """
        Test that a repeating chunk event shows up on 'day' list view when
        it's supposed to.
        """
        event = create_event(
            start_date=(2014, 2, 28),
            end_date=(2014, 3, 2),
            created_by=self.user,
            title="Samantha",
            description="nice event",
            repeat="WEEKLY"
        )
        for year in range(2014, 2015):
            response = self.client.get(reverse(
                'calendar:day_list',
                kwargs={'year': year, 'month': '2', 'day': '28'}
            ))
            self.assertContains(response, event.title)

        for year in range(2014, 2015):
            for day in (1, 2, 3, 7, 8, 9):
                response = self.client.get(reverse(
                    'calendar:day_list',
                    kwargs={'year': '2014', 'month': '3', 'day': day}
                ))
                if day == 3:
                    self.assertNotContains(response, event.title)
                else:
                    self.assertContains(response, event.title)

    def test_list_view_invalid_date(self):
        response = self.client.get(
            reverse(
                'calendar:day_list',
                kwargs={'year': '2014', 'month': '2', 'day': '80'}
            )
        )
        self.assertContains(response, 'The date given was invalid')

    def test_list_view_category_and_tag_querystrings(self):
        response = self.client.get(
            reverse(
                'calendar:day_list',
                kwargs={'year': '2014', 'month': '2', 'day': '28'}
            ),
            {'cal_category': 'birthdays', 'cal_tag': 'doggies'}
        )
        self.assertContains(response, 'birthdays')
        self.assertContains(response, 'doggies')

    def test_day_list_view_cancelled_event(self):
        """Test that a cancelled event displays correctly."""
        event = create_event(
            start_date=(2014, 5, 15),
            end_date=(2014, 5, 15),
            created_by=self.user,
            title="Elspeth",
            description="Angelic Event."
        )
        event.cancellations.create(
            reason="Terror",
            date=date(2014, 5, 15)
        )
        response = self.client.get(reverse(
            'calendar:day_list',
            kwargs={'year': '2014', 'month': '5', 'day': '15'}
        ))
        self.assertContains(response, event.title + ' (CANCELLED)')
