from __future__ import unicode_literals

from calendar import monthrange
import datetime

from django.core.urlresolvers import reverse
from django.utils.six.moves import xrange

from .event_factory import create_event, SetMeUp


class WeeklyRepeatingChunkEventListViewTest(SetMeUp):
    """Test repeating 'chunk' events"""
    def check_dates(self, event, valid_dates):
        """A DRY helper function."""
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

    def test_weekly_repeating_chunk_two_days_span_two_months(self):
        """
        Test that a weekly repeating chunk that lasts two days and
        spans 2 different months when it starts will honor end_repeat.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Ruby",
            description="'chunk' event that lasts 5 days and repeats weekly.",
            repeat="WEEKLY",
            end_repeat=datetime.date(2015, 4, 27)
        )
        valid_dates = {
            '2014': {
                '03': [31],
                '04': [1, 7, 8, 14, 15, 21, 22, 28, 29],
                '05': [5, 6, 12, 13, 19, 20, 26, 27],
                '06': [2, 3, 9, 10, 16, 17, 23, 24, 30],
                '07': [1, 7, 8, 14, 15, 21, 22, 28, 29],
                '08': [4, 5, 11, 12, 18, 19, 25, 26],
                '09': [1, 2, 8, 9, 15, 16, 22, 23, 29, 30],
                '10': [6, 7, 13, 14, 20, 21, 27, 28],
                '11': [3, 4, 10, 11, 17, 18, 24, 25],
                '12': [1, 2, 8, 9, 15, 16, 22, 23, 29, 30]
            },
            '2015': {
                '01': [5, 6, 12, 13, 19, 20, 26, 27],
                '02': [2, 3, 9, 10, 16, 17, 23, 24],
                '03': [2, 3, 9, 10, 16, 17, 23, 24, 30, 31],
                '04': [6, 7, 13, 14, 20, 21, 27],
                '05': []
            }
        }
        self.check_dates(event, valid_dates)

    def test_weekly_repeating_chunk_six_days_span_two_months(self):
        """
        Test a weekly repeating chunk that lasts six days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 28),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Khloe",
            description="'chunk' event that lasts 6 days and repeats weekly.",
            repeat="WEEKLY"
        )
        invalid_dates = {
            '2014': {
                '04': [3, 10, 17, 24],
                '05': [1, 8, 15, 22, 29],
                '06': [5, 12, 19, 26],
                '07': [3, 10, 17, 24, 31],
                '08': [7, 14, 21, 28],
                '09': [4, 11, 18, 25],
                '10': [2, 9, 16, 23, 30],
                '11': [6, 13, 20, 27],
                '12': [4, 11, 18, 25],
            },
            '2015': {
                '01': [1, 8, 15, 22, 29],
                '02': [5, 12, 19, 26],
                '03': [5, 12, 19, 26],
                '04': [2, 9, 16, 23, 30],
            }
        }

        for year, dates in invalid_dates.items():
            for month, days in dates.items():
                response = self.client.get(reverse(
                    'calendar:list', kwargs={'year': year, 'month': month}
                ))
                self.clean_whitespace(response)
                self.assertContains(response, event.title)

                for day in days:
                    self.assertNotContains(response, self.cal_str(day))

                [self.assertContains(response, self.cal_str(day)) for
                 day in xrange(1, monthrange(2014, int(month))[1] + 1)
                 if day not in days]

    def test_weekly_repeating_chunk_three_days_span_one_month(self):
        """
        Test a weekly repeating chunk that lasts two days with
        start_date and end_date in the same month, and the event scheduled
        early in the month.
        """
        event = create_event(
            start_date=(2014, 2, 3),
            end_date=(2014, 2, 5),
            created_by=self.user,
            title="Jona",
            description="'chunk' event that lasts 3 days and repeats weekly.",
            repeat="WEEKLY"
        )
        valid_dates = {
            '2014': {
                '02': [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26],
                '03': [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26, 31],
                '04': [1, 2, 7, 8, 9, 14, 15, 16, 21, 22, 23, 28, 29, 30],
                '05': [5, 6, 7, 12, 13, 14, 19, 20, 21, 26, 27, 28],
                '06': [2, 3, 4, 9, 10, 11, 16, 17, 18, 23, 24, 25, 30],
                '07': [1, 2, 7, 8, 9, 14, 15, 16, 21, 22, 23, 28, 29, 30],
                '08': [4, 5, 6, 11, 12, 13, 18, 19, 20, 25, 26, 27],
                '09': [1, 2, 3, 8, 9, 10, 15, 16, 17, 22, 23, 24, 29, 30],
                '10': [1, 6, 7, 8, 13, 14, 15, 20, 21, 22, 27, 28, 29],
                '11': [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26],
                '12': [1, 2, 3, 8, 9, 10, 15, 16, 17, 22, 23, 24, 29, 30, 31],
            },
            '2015': {
                '01': [5, 6, 7, 12, 13, 14, 19, 20, 21, 26, 27, 28],
                '02': [2, 3, 4, 9, 10, 11, 16, 17, 18, 23, 24, 25],
                '03': [2, 3, 4, 9, 10, 11, 16, 17, 18, 23, 24, 25, 30, 31]
            }
        }
        self.check_dates(event, valid_dates)

    def test_weekly_repeating_chunk_three_days_span_one_month2(self):
        """
        Test a weekly repeating chunk that lasts two days with
        start_date and end_date in the same month, and the event scheduled
        early in the month.
        """
        event = create_event(
            start_date=(2014, 3, 14),
            end_date=(2014, 3, 16),
            created_by=self.user,
            title="Carmine",
            description="'chunk' event that lasts 3 days and repeats weekly.",
            repeat="WEEKLY"
        )
        valid_dates = {
            '2014': {
                '03': [14, 15, 16, 21, 22, 23, 28, 29, 30],
                '04': [4, 5, 6, 11, 12, 13, 18, 19, 20, 25, 26, 27],
                '05': [2, 3, 4, 9, 10, 11, 16, 17, 18, 23, 24, 25, 30, 31],
                '06': [1, 6, 7, 8, 13, 14, 15, 20, 21, 22, 27, 28, 29],
                '07': [4, 5, 6, 11, 12, 13, 18, 19, 20, 25, 26, 27],
                '08': [1, 2, 3, 8, 9, 10, 15, 16, 17, 22, 23, 24, 29, 30, 31],
                '09': [5, 6, 7, 12, 13, 14, 19, 20, 21, 26, 27, 28],
                '10': [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26, 31],
                '11': [1, 2, 7, 8, 9, 14, 15, 16, 21, 22, 23, 28, 29, 30],
            }
        }
        self.check_dates(event, valid_dates)

    def test_weekly_repeating_chunk_three_days_span_one_month3(self):
        """
        Test a weekly repeating chunk that lasts seven days with
        start_date and end_date in the same month. This should result in
        every day in the month being filled in.
        """
        event = create_event(
            start_date=(2014, 3, 25),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Snoop",
            description="Erry day",
            repeat="WEEKLY"
        )
        days_31 = [x for x in xrange(1, 32)]
        days_30 = [x for x in xrange(1, 31)]
        dm = dict.fromkeys(['5', '7', '8', '10', '12'], days_31)
        dm2 = dict.fromkeys(['6', '9', '11'], days_30)
        dm.update(dm2)
        valid_dates = dict.fromkeys(['2014', '2015'], dm)
        self.check_dates(event, valid_dates)

    def test_weekly_repeating_chunk_three_days_span_one_month_end_repeat(self):
        """
        Test that a weekly repeating chunk honors an end_repeat
        during the first week of a month.
        """
        event = create_event(
            start_date=(2014, 2, 3),
            end_date=(2014, 2, 5),
            created_by=self.user,
            title="Gaga",
            description="'chunk' event. Weekly repeat w/ end_repeat.",
            repeat="WEEKLY",
            end_repeat=datetime.date(2014, 3, 4)
        )
        valid_dates = {
            '2014': {
                '02': [3, 4, 5, 10, 11, 12, 17, 18, 19, 24, 25, 26],
                '03': [3, 4], '04': []
            }
        }
        self.check_dates(event, valid_dates)
