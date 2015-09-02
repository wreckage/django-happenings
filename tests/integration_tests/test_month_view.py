from __future__ import unicode_literals

from calendar import month_name
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils import timezone
from django.utils import six

from .event_factory import create_event, SetMeUp
from happenings.utils import displays


HTML = 'class="calendar-event"'


@override_settings(CALENDAR_SHOW_LIST=True)
class NoEventTest(TestCase):
    def test_list_view_with_no_events(self):
        """
        If there are no events, an appropriate message should be displayed.
        """
        response = self.client.get(reverse('calendar:list'))
        self.assertContains(response, "No events")

    def test_list_view_with_empty_category(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_category': 'foo'}
        )
        self.assertContains(response, "No events")

    def test_list_view_with_no_tags(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_tag': 'bar'}
        )
        self.assertContains(response, "No events")


class EventListViewTest(SetMeUp):
    def setUp(self):
        create_event(
            created_by=self.user,
            title="Category and tag",
            description="I have a category and a tag.",
        )

        create_event(
            created_by=self.user,
            title="Category no tag",
            description="I have a category but no tags.",
        )

        create_event(
            created_by=self.user,
            title="Tag no category",
            description="I have a tag but no category.",
        )

    def test_list_view_with_multiple_events(self):
        """This should list all of the events."""
        response = self.client.get(reverse('calendar:list'))
        self.assertContains(response, "Category no tag")
        self.assertContains(response, "Tag no category")
        self.assertContains(response, "Category and tag")
        self.assertContains(response, HTML)

    def test_list_view_with_no_event_for_next_month(self):
        """
        The only events created so far are for this month, so next month should
        have none.
        """
        response = self.client.get(reverse('calendar:list'), {'cal_next': 1})
        self.assertContains(response, "No events")
        self.assertNotContains(response, "calendar-event")


class EventListViewDisplayTest(SetMeUp):
    def test_list_view_year_and_month_in_url(self):
        """
        Let's make sure that an event will only display when the correct
        year and month are entered into the url, so that an event in e.g.
        February of 2015 doesn't show up in February of 2014, 2016, etc.
        but will show up if url looks like: /calendar/2015/02/
        """
        event1 = create_event(
            start_date=(2015, 2, 15),
            end_date=(2015, 2, 16),
            created_by=self.user,
            title="Next month event",
            description="This is an event for next month."
        )
        event2 = create_event(
            start_date=(2015, 2, 15),
            end_date=(2015, 2, 16),
            created_by=self.user,
            title="Next month event part deux",
            description="This is an event for next month."
        )

        years = ['2010', '2015', '2020']
        for year in years:
            response = self.client.get(reverse(
                'calendar:list', kwargs={'year': year, 'month': '02'}
            ))
            if year == '2015':
                self.assertContains(response, event1.title)
                self.assertContains(response, event2.title)
                self.assertContains(response, HTML)
            else:
                self.assertNotContains(response, 'calendar-event')

    def test_list_view_incorrect_year_and_or_month_in_url(self):
        """
        A month < 01 should give 404, a month > 01 should redirect
        and display an error message.
        A year that is outside of the current year +/- 50 years
        should also redirect and display an error message.
        """
        message = "invalid"
        dates = {'2015': '00', '2015': '42', '1015': '01', '4015': '22'}
        for year, month in six.iteritems(dates):
            response = self.client.get(reverse(
                'calendar:list', kwargs={'year': year, 'month': month}
            ))
            self.assertContains(response, message)

    def test_list_view_calendar_starts_different_day(self):
        """Test that the calendar can start on different days."""
        # start on Monday
        cal = displays.month_display(
            2014, 3, [], 0, 0, ''
        )
        s = '</a></th></tr><tr><th class="mon">Mon</th><th class="tue"'
        self.assertIn(s, self.clean_whitespace(cal))

        # start on Sunday
        cal = displays.month_display(
            2014, 3, [], 6, 0, ''
        )
        s = '</a></th></tr><tr><th class="sun">Sun</th><th class="mon"'
        self.assertIn(s, self.clean_whitespace(cal))

    def test_list_view_calendar_current_day(self):
        """
        Test that the calendar gives a unique class to a day if that day
        is the current day.
        """
        response = self.client.get(reverse('calendar:list'))
        self.assertContains(response, "calendar-today")
        response = self.client.get(reverse('calendar:list'), {'cal_next': '1'})
        self.assertNotContains(response, "calendar-today")
        response = self.client.get(
            reverse('calendar:list'), {'cal_next': '12'}
        )
        self.assertNotContains(response, "calendar-today")

    def test_list_view_calendar_preserve_querystrings(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_category': 'birthday'}
        )
        self.assertContains(response, "cal_next=1&cal_category=birthday")
        self.assertContains(response, "cal_prev=1&cal_category=birthday")

    def test_list_view_cal_ignore_querystrings(self):
        """cal_ignore qs should set time to now."""
        response = self.client.get(
            reverse('calendar:list'), {'cal_ignore': 'true'}
        )
        self.assertContains(response, month_name[timezone.now().month])
        self.assertContains(response, timezone.now().year)

    def test_list_view_calendar_year_month_in_url(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_month': '2', 'cal_year': '2012'}
        )
        self.assertContains(response, "February")
        self.assertContains(response, "2012")
