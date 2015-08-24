from __future__ import unicode_literals

from calendar import monthrange
import datetime

from django.core.urlresolvers import reverse
from django.utils.six.moves import xrange

from .event_factory import create_event, SetMeUp


class MonthlyRepeatingChunkEventListViewTest(SetMeUp):
    """Test monthly repeating 'chunk' events"""
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

    def test_monthly_repeating_chunk_two_days_span_two_months(self):
        """
        Test a monthly repeating chunk that lasts two days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="John",
            description="'chunk' event that lasts 2 days and repeats monthly.",
            repeat="MONTHLY"
        )
        valid_dates = {
            '2014': {'03': [31], '04': [1], '05': [31], '06': [1],
                     '07': [31], '08': [1, 31], '09': [1], '10': [31],
                     '11': [1], '12': [31]},
            '2015': {'01': [1, 31], '02': [1], '03': [31], '04': [1]}
        }
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_six_days_span_two_months(self):
        """
        Test a monthly repeating chunk that lasts six days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 28),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Paul",
            description="'chunk' event that lasts 6 days and repeats monthly.",
            repeat="MONTHLY"
        )
        x = [1, 2, 28, 29, 30]
        y = [1, 2, 28, 29, 30, 31]
        valid_dates = {
            '2014': {'03': [28, 29, 30, 31], '04': x, '05': y, '06': x,
                     '07': y, '08': y, '09': x, '10': y, '11': x, '12': y},
            '2015': {'01': y, '02': [1, 2, 28], '03': y, '04': x}
        }
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_three_days_span_one_month(self):
        """
        Test a monthly repeating chunk that lasts three days with
        start_date and end_date in the same month.
        """
        event = create_event(
            start_date=(2014, 1, 3),
            end_date=(2014, 1, 5),
            created_by=self.user,
            title="Mary",
            description="chunk event that lasts 3 days and repeats monthly.",
            repeat="MONTHLY"
        )
        d = [3, 4, 5]
        m = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
             '10', '11', '12']
        valid_dates = {
            '2014': dict.fromkeys(m, d), '2015': dict.fromkeys(m, d),
        }
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_three_days_span_one_month2(self):
        """
        Test a monthly repeating chunk that lasts two days with
        start_date and end_date in the same month.
        """
        event = create_event(
            start_date=(2014, 1, 14),
            end_date=(2014, 1, 16),
            created_by=self.user,
            title="Mufasa",
            description="chunk event that lasts 3 days and repeats monthly.",
            repeat="MONTHLY"
        )
        d = [14, 15, 16]
        m = ['01', '02', '03', '04', '05', '06', '07', '08', '09',
             '10', '11', '12']
        valid_dates = {
            '2014': dict.fromkeys(m, d), '2015': dict.fromkeys(m, d),
        }
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_three_days_span_one_month3(self):
        """
        Test a monthly repeating chunk that lasts three days with
        start_date and end_date in the same month, but with the event
        ending on the 31st. This checks that we the calendar won't complain
        if the event runs off the end of the month sometimes, and it shouldn't
        add those extra days to the beginning of the following month.
        """
        event = create_event(
            start_date=(2014, 3, 25),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Arnie",
            description="chunk event that lasts 3 days and repeats monthly.",
            repeat="MONTHLY"
        )
        x = [i for i in xrange(25, 32)]
        y = [i for i in xrange(25, 31)]
        z = {'03': x, '04': y, '05': x}
        valid_dates = dict.fromkeys(['2014', '2015', '2016'], z)
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_with_end_repeat(self):
        """
        Test that a monthly repeating chunk honors end_repeat
        """
        event = create_event(
            start_date=(2014, 3, 14),
            end_date=(2014, 3, 16),
            created_by=self.user,
            title="Simba",
            description="chunk event that lasts 3 days and repeats monthly.",
            repeat="MONTHLY",
            end_repeat=datetime.date(2014, 5, 15)
        )
        valid_dates = {
            '2014': {
                '03': [14, 15, 16],
                '04': [14, 15, 16],
                '05': [14, 15],
                '06': []
            }
        }
        self.check_dates(event, valid_dates)

    def test_monthly_repeating_chunk_with_end_repeat2(self):
        """
        Test that a monthly repeating chunk honors an end_repeat at
        the beginning of the month for an event that spans 2 months
        when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Timon",
            description="testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=datetime.date(2014, 6, 1)
        )
        valid_dates = {
            '2014': {'03': [31], '04': [1, 2], '05': [31], '06': [1], '07': []}
        }
        self.check_dates(event, valid_dates)
