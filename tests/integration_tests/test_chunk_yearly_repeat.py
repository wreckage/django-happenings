from __future__ import unicode_literals

from calendar import monthrange
import datetime

from django.core.urlresolvers import reverse
from django.utils.six.moves import xrange

from .event_factory import create_event, SetMeUp


class YearlyRepeatingChunkEventListViewTest(SetMeUp):
    """Test yearly repeating 'chunk' events"""
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

    def test_yearly_repeating_chunk_two_days_span_two_months(self):
        """
        Test a yearly repeating chunk that lasts two days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 1),
            created_by=self.user,
            title="Theodore",
            description="'chunk' event that lasts 2 days and repeats yearly.",
            repeat="YEARLY"
        )
        valid_dates = {
            '2014': {'03': [31], '04': [1], '05': []},
            '2015': {'03': [31], '04': [1], '05': []},
            '2016': {'03': [31], '04': [1], '05': []}
        }
        self.check_dates(event, valid_dates)

    def test_yearly_repeating_chunk_six_days_span_two_months(self):
        """
        Test a yearly repeating chunk that lasts six days and
        spans 2 different months when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 28),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Alvin",
            description="'chunk' event that lasts 6 days and repeats yearly.",
            repeat="YEARLY"
        )
        valid_dates = {
            '2014': {'03': [28, 29, 30, 31], '04': [1, 2], '05': []},
            '2015': {'03': [28, 29, 30, 31], '04': [1, 2], '05': []},
            '2016': {'03': [28, 29, 30, 31], '04': [1, 2], '05': []}
        }
        self.check_dates(event, valid_dates)

    def test_yearly_repeating_chunk_three_days_span_one_month(self):
        """
        Test a monthly repeating chunk that lasts three days with
        start_date and end_date in the same month.
        """
        event = create_event(
            start_date=(2014, 1, 27),
            end_date=(2014, 1, 28),
            created_by=self.user,
            title="Omar",
            description="chunk event that lasts 3 days and repeats yearly.",
            repeat="YEARLY"
        )
        valid_dates = {
            '2014': {'01': [27, 28], '02': []},
            '2015': {'01': [27, 28], '02': []},
        }
        self.check_dates(event, valid_dates)

    def test_yearly_repeating_chunk_with_end_repeat(self):
        """
        Test that a yearly repeating chunk honors end_repeat
        """
        event = create_event(
            start_date=(2014, 3, 14),
            end_date=(2014, 3, 16),
            created_by=self.user,
            title="Clive",
            description="chunk event that lasts 3 days and repeats yearly.",
            repeat="YEARLY",
            end_repeat=datetime.date(2016, 3, 15)
        )
        valid_dates = {
            '2014': {'02': [], '03': [14, 15, 16], '04': []},
            '2015': {'02': [], '03': [14, 15, 16], '04': []},
            '2016': {'02': [], '03': [14, 15], '04': []},
            '2017': {'02': [], '03': [], '04': []},
        }
        self.check_dates(event, valid_dates)

    def test_yearly_repeating_chunk_with_end_repeat2(self):
        """
        Test that a yearly repeating chunk honors an end_repeat at
        the beginning of the month for an event that spans 2 months
        when it starts.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 4, 2),
            created_by=self.user,
            title="Simon",
            description="testing 1 2 3",
            repeat="YEARLY",
            end_repeat=datetime.date(2016, 4, 1)
        )
        valid_dates = {
            '2014': {'03': [31], '04': [1, 2], '05': []},
            '2015': {'03': [31], '04': [1, 2], '05': []},
            '2016': {'03': [31], '04': [1], '05': []}
        }
        self.check_dates(event, valid_dates)
