from __future__ import unicode_literals

import re
import datetime
from calendar import monthrange

from django.core.urlresolvers import reverse
from django.utils.six.moves import xrange

from .event_factory import create_event, SetMeUp


class RepeatingEventListViewTest(SetMeUp):
    def check_dates_yearly(self, event, valid_dates):
        """A DRY helper function for yearly repeat tests."""
        for year, dates in valid_dates.items():
            for month, days in dates.items():
                response = self.client.get(reverse(
                    'calendar:list', kwargs={'year': year, 'month': month}
                ))
                self.clean_whitespace(response)
                if days:
                    self.assertContains(response, event.title)
                else:
                    self.assertNotContains(response, event.title)

                for day in days:
                    self.assertContains(response, self.cal_str(day))

                [self.assertNotContains(response, self.cal_str(day)) for
                 day in xrange(1, monthrange(2014, int(month))[1] + 1)
                 if day not in days]

    def check_dates(self, valid_dates, title, one_year=True):
        """
        Checks the dates in the given valid_dates dict. Also check that the
        event title appears on the page when it's supposed to.
        """
        for year, dates in valid_dates.items():
            for month, days in dates.items():
                response = self.client.get(reverse(
                    'calendar:list', kwargs={'year': year, 'month': month}
                ))
                self.clean_whitespace(response)
                if days:
                    self.assertContains(response, title)
                else:
                    self.assertNotContains(response, title)

                for day in days:
                    # days given should appear on the calendar
                    [self.assertContains(response, self.cal_str(day)) for
                     day in days]
                    # days not given should not appear on the calendar
                    [self.assertNotContains(response, self.cal_str(day)) for
                     day in xrange(1, monthrange(2014, int(month))[1] + 1)
                     if day not in days]
                if one_year:
                    response = self.client.get(reverse(
                        'calendar:list', kwargs={
                            'year': str(int(year) + 1), 'month': month
                        }
                    ))
                    self.clean_whitespace(response)
                    self.assertNotContains(response, title)

            # all the events are scheduled for 2014, so 2015 shouldn't see any
            # response = self.client.get(reverse(
            #     'calendar:list', kwargs={'year': '2015', 'month': month}
            # ))
            # self.assertNotContains(response, title)

    def create_event_start_this_month_end_this_month(self, repeat):
        event = create_event(
            start_date=(2014, 2, 15),
            end_date=(2014, 2, 15),
            created_by=self.user,
            title="Charlie",
            description="I start and end repeat in the same month.",
            repeat=repeat,
            end_repeat=datetime.date(2014, 2, 22)
        )
        return event

    def create_event_start_this_month_end_in_two_months(self, repeat):
        event = create_event(
            start_date=(2014, 2, 15),
            end_date=(2014, 2, 15),
            created_by=self.user,
            title="Frank",
            description="I start and end repeat in the same month.",
            repeat=repeat,
            end_repeat=datetime.date(2014, 4, 20)
        )
        return event

    def create_event_repeat_forever(self, repeat):
        event = create_event(
            start_date=(2014, 1, 2),
            end_date=(2014, 1, 2),
            created_by=self.user,
            title="Foo",
            description="I start and never end.",
            repeat=repeat,
        )
        return event

    def test_weekly_repeating_event_only_appears_once(self):
        """
        Tests that a weekly repeating event only appears once.
        This test written after a bug was discovered on May 29, 2014.
        The bug was created during the switch to a more OO design, and involved
        count_first being incorrectly set to True.
        """
        create_event(
            start_date=(2014, 5, 26),
            end_date=(2014, 5, 26),
            created_by=self.user,
            title="Whoa",
            description="Single event",
            repeat="WEEKLY",
        )
        response = self.client.get(reverse(
            'calendar:list', kwargs={'year': '2014', 'month': '5'}
        ))
        self.clean_whitespace(response)
        match = re.findall('May 26,12:00AM - 12:00AM', str(response.content))
        self.assertEqual(1, len(match))

    def test_list_view_with_never_ending_weekly_repeat(self):
        event = self.create_event_repeat_forever('WEEKLY')
        valid_dates = {
            '2014': {
                '01': [2, 9, 16, 23, 30],
                '02': [6, 13, 20, 27],
                '03': [6, 13, 20, 27],
                '04': [3, 10, 17, 24],
                '12': [4, 11, 18, 25],
            },
            '2015': {
                '01': [1, 8, 15, 22, 29],
                '02': [5, 12, 19, 26],
            }
        }
        self.check_dates(valid_dates, event.title, one_year=False)

    def test_list_view_with_weekly_repeat(self):
        event = self.create_event_start_this_month_end_in_two_months('WEEKLY')
        valid_dates = {
            '2014': {
                '02': [15, 22], '03': [1, 8, 15, 22, 29],
                '04': [5, 12, 19],
                '05': []
            },
        }
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_weekly_repeat_2(self):
        event = self.create_event_start_this_month_end_this_month('WEEKLY')
        valid_dates = {'2014': {'02': [15, 22], '03': []}}
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_never_ending_biweekly_repeat(self):
        event = self.create_event_repeat_forever('BIWEEKLY')
        valid_dates = {
            '2014': {
                '01': [2, 16, 30],
                '02': [13, 27],
                '03': [13, 27],
                '12': [4, 18],
            },
            '2015': {
                '01': [1, 15, 29],
                '02': [12, 26]
            }
        }
        self.check_dates(valid_dates, event.title, one_year=False)

    def test_list_view_with_biweekly_repeat(self):
        event = self.create_event_start_this_month_end_in_two_months(
            'BIWEEKLY')
        valid_dates = {
            '2013': {'02': [], '03': []},
            '2014': {
                '02': [15], '03': [1, 15, 29], '04': [12], '05': []
            }
        }
        self.check_dates(valid_dates, event.title, one_year=False)

    def test_list_view_with_biweekly_repeat_2(self):
        event = self.create_event_start_this_month_end_this_month('BIWEEKLY')
        valid_dates = {'2014': {'02': [15], '03': []}}
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_never_ending_monthly_repeat(self):
        event = self.create_event_repeat_forever('MONTHLY')
        d = [2]
        m = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
             '10', '11', '12']
        valid_dates = {
            '2013': {'01': [], '03': [], '05': []},
            '2014': dict.fromkeys(m, d),
            '2015': dict.fromkeys(m, d),
        }
        self.check_dates(valid_dates, event.title, one_year=False)

    def test_list_view_with_monthly_repeat(self):
        event = self.create_event_start_this_month_end_in_two_months('MONTHLY')
        valid_dates = {'2014': {'02': [15], '03': [15], '04': [15], '05': []}}
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_monthly_repeat_2(self):
        event = self.create_event_start_this_month_end_this_month('MONTHLY')
        valid_dates = {'2014': {'02': [15], '03': []}}
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_yearly_repeat(self):
        event = create_event(
            start_date=(2014, 3, 15),
            end_date=(2014, 3, 15),
            created_by=self.user,
            title="Courtney",
            description="I repeat yearly with no end_repeat.",
            repeat='YEARLY',
        )
        valid_dates = {
            '2013': {'02': [], '03': [], '04': [], '05': []},
            '2014': {'02': [], '03': [15], '04': [], '05': []},
            '2015': {'02': [], '03': [15], '04': [], '05': []},
            '2016': {'02': [], '03': [15], '04': [], '05': []},
        }
        # to save time, let's not test every month of the year
        self.check_dates_yearly(event, valid_dates)

    def test_list_view_with_yearly_repeat_2(self):
        event = create_event(
            start_date=(2014, 3, 15),
            end_date=(2014, 3, 15),
            created_by=self.user,
            title="Brittney",
            description="I repeat yearly for 2 years.",
            repeat='YEARLY',
            end_repeat=datetime.date(2016, 3, 15)
        )
        valid_dates = {
            '2014': {'02': [], '03': [15], '04': []},
            '2015': {'02': [], '03': [15], '04': []},
            '2016': {'02': [], '03': [15], '04': []},
            '2017': {'02': [], '03': [], '04': []},
        }
        self.check_dates_yearly(event, valid_dates)

    def test_list_view_with_daily_repeat(self):
        event = create_event(
            start_date=(2014, 4, 1),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Casey",
            description="I repeat every day with no end in sight.",
            repeat='DAILY',
        )
        m = ['04', '05', '06']
        y = ['2014', '2015', '2016']
        valid_dates = dict.fromkeys(y, m)
        for year, months in valid_dates.items():
            for month in months:
                response = self.client.get(reverse(
                    'calendar:list', kwargs={'year': year, 'month': month}
                ))
                self.clean_whitespace(response)
                self.assertContains(response, event.title)
                [self.assertContains(response, self.cal_str(day)) for
                 day in xrange(1, monthrange(2014, int(month) + 1)[1])]

        # The month before start_date shouldn't have any events
        response = self.client.get(reverse(
            'calendar:list', kwargs={'year': '2014', 'month': '03'}
        ))
        self.clean_whitespace(response)
        self.assertNotContains(response, event.title)
        self.assertNotContains(response, self.event_div)

    def test_list_view_with_daily_repeat_and_end_repeat(self):
        event = create_event(
            start_date=(2014, 4, 1),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Casey",
            description="I repeat daily and end later in the month.",
            repeat='DAILY',
            end_repeat=datetime.date(2014, 4, 22),
        )
        x = [i + 1 for i in xrange(22)]
        valid_dates = {'2014': {'04': x, '05': []}}
        self.check_dates(valid_dates, event.title)

    def test_list_view_with_weekday_repeat(self):
        event = create_event(
            start_date=(2014, 4, 1),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Monica",
            description="I repeat every weekday with no end in sight.",
            repeat='WEEKDAY',
        )
        valid_dates = {
            '2014': {
                '04': [1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18,
                       21, 22, 23, 24, 25, 28, 29, 30]
            }
        }
        self.check_dates(valid_dates, event.title, one_year=False)
