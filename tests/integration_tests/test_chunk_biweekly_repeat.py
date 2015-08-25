from __future__ import unicode_literals

from calendar import monthrange
import datetime

from django.core.urlresolvers import reverse
from django.utils.six.moves import xrange

from .event_factory import create_event, SetMeUp


class BiweeklyRepeatingChunkEventListViewTest(SetMeUp):
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

    def test_biweekly_repeating_chunk_two_days_span_two_months(self):
        """
        Test a biweekly repeating chunk that lasts two days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Ruby",
            description="'chunk' event that lasts 2 days and repeats weekly.",
            repeat="BIWEEKLY"
        )
        valid_dates = {
            '2014': {
                '03': [31],
                '04': [1, 14, 15, 28, 29],
                '05': [12, 13, 26, 27],
                '06': [9, 10, 23, 24],
                '07': [7, 8, 21, 22],
                '08': [4, 5, 18, 19],
                '09': [1, 2, 15, 16, 29, 30],
                '10': [13, 14, 27, 28],
                '11': [10, 11, 24, 25],
                '12': [8, 9, 22, 23]
            },
            '2015': {
                '01': [5, 6, 19, 20],
                '02': [2, 3, 16, 17],
                '03': [2, 3, 16, 17, 30, 31],
                '04': [13, 14, 27, 28],
            }
        }
        self.check_dates(event, valid_dates)

    def test_biweekly_repeating_chunk_six_days_span_two_months(self):
        """
        Test a biweekly repeating chunk that lasts six days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 28),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Fred",
            description="'chunk' event that lasts 6 days and repeats weekly.",
            repeat="BIWEEKLY"
        )
        valid_dates = {
            '2014': {
                '03': [28, 29, 30, 31],
                '04': [1, 2, 11, 12, 13, 14, 15, 16, 25, 26, 27, 28, 29, 30],
                '05': [9, 10, 11, 12, 13, 14, 23, 24, 25, 26, 27, 28],
                '06': [6, 7, 8, 9, 10, 11, 20, 21, 22, 23, 24, 25],
                '07': [4, 5, 6, 7, 8, 9, 18, 19, 20, 21, 22, 23],
                '08': [1, 2, 3, 4, 5, 6, 15, 16, 17, 18, 19, 20, 29, 30, 31],
                '09': [1, 2, 3, 12, 13, 14, 15, 16, 17, 26, 27, 28, 29, 30],
                '10': [1, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29],
                '11': [7, 8, 9, 10, 11, 12, 21, 22, 23, 24, 25, 26],
                '12': [5, 6, 7, 8, 9, 10, 19, 20, 21, 22, 23, 24],
            },
            '2015': {
                '01': [2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 30, 31],
                '02': [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 27, 28],
                '03': [1, 2, 3, 4, 13, 14, 15, 16, 17, 18, 27, 28, 29, 30, 31],
                '04': [1, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29],
            }
        }
        self.check_dates(event, valid_dates)

    def test_biweekly_repeating_chunk_three_days_span_one_month(self):
        """
        Test a biweekly repeating chunk that lasts three days with
        start_date and end_date in the same month, and the event scheduled
        early in the month.
        """
        event = create_event(
            start_date=(2014, 2, 3),
            end_date=(2014, 2, 5),
            created_by=self.user,
            title="Maria",
            description="chunk event that lasts 3 days and repeats biweekly.",
            repeat="BIWEEKLY"
        )
        valid_dates = {
            '2014': {
                '02': [3, 4, 5, 17, 18, 19],
                '03': [3, 4, 5, 17, 18, 19, 31],
                '04': [1, 2, 14, 15, 16, 28, 29, 30],
                '05': [12, 13, 14, 26, 27, 28],
                '06': [9, 10, 11, 23, 24, 25],
                '07': [7, 8, 9, 21, 22, 23],
                '08': [4, 5, 6, 18, 19, 20],
                '09': [1, 2, 3, 15, 16, 17, 29, 30],
                '10': [1, 13, 14, 15, 27, 28, 29],
                '11': [10, 11, 12, 24, 25, 26],
                '12': [8, 9, 10, 22, 23, 24],
            },
            '2015': {
                '01': [5, 6, 7, 19, 20, 21],
                '02': [2, 3, 4, 16, 17, 18],
                '03': [2, 3, 4, 16, 17, 18, 30, 31],
            }
        }
        self.check_dates(event, valid_dates)

    def test_biweekly_repeating_chunk_three_days_span_one_month2(self):
        """
        Test a weekly repeating chunk that lasts two days with
        start_date and end_date in the same month, and the event scheduled
        early in the month.
        """
        event = create_event(
            start_date=(2014, 3, 14),
            end_date=(2014, 3, 16),
            created_by=self.user,
            title="Scar",
            description="chunk event that lasts 3 days and repeats biweekly.",
            repeat="BIWEEKLY"
        )
        valid_dates = {
            '2014': {
                '03': [14, 15, 16, 28, 29, 30],
                '04': [11, 12, 13, 25, 26, 27],
                '05': [9, 10, 11, 23, 24, 25],
                '06': [6, 7, 8, 20, 21, 22],
                '07': [4, 5, 6, 18, 19, 20],
                '08': [1, 2, 3, 15, 16, 17, 29, 30, 31],
                '09': [12, 13, 14, 26, 27, 28],
                '10': [10, 11, 12, 24, 25, 26],
                '11': [7, 8, 9, 21, 22, 23],
                '12': [5, 6, 7, 19, 20, 21],
            },
            '2015': {
                '01': [2, 3, 4, 16, 17, 18, 30, 31],
                '02': [1, 13, 14, 15, 27, 28],
                '03': [1, 13, 14, 15, 27, 28, 29],
            }
        }
        self.check_dates(event, valid_dates)

    def test_biweekly_repeating_chunk_with_end_repeat(self):
        """
        Test that a biweekly repeating chunk honors end_repeat.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Chelsea",
            description="I should end on end_repeat.",
            repeat="BIWEEKLY",
            end_repeat=datetime.date(2014, 6, 9)
        )
        valid_dates = {
            '2014': {
                '03': [31],
                '04': [1, 14, 15, 28, 29],
                '05': [12, 13, 26, 27],
                '06': [9],
                '07': [],
            },
            '2015': {'01': [], '03': [], '04': []}
        }
        self.check_dates(event, valid_dates)
