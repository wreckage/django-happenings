from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone

now = timezone.localtime(timezone.now())

from happenings.utils.common import clean_year_month_day, clean_year_month

ERROR = "The date given was invalid."


class CleanYearMonthTest(TestCase):
    """Tests the clean_year_month() utility function"""
    def test_valid(self):
        year, month, error = clean_year_month(2014, 3, 3)
        self.assertEqual(year, 2014)
        self.assertEqual(month, 3)
        self.assertEqual(error, False)

    def test_fix_year_month_next(self):
        """
        Test that it subtracts from month and adds to year to fix date
        when a 'next' querystring makes month > 12.
        """
        # 13 - 10 = next query of 3
        year, month, error = clean_year_month(2014, 13, 10)
        self.assertEqual(year, 2015)
        self.assertEqual(month, 1)
        self.assertEqual(error, False)

    def test_fix_year_month_next_gt_12(self):
        """
        Test that it subtracts from month and adds to year to fix date
        when a 'next' querystring makes month > 12 (w/ next qs > 12).
        """
        # 23 - 10 = next query of 13
        year, month, error = clean_year_month(2014, 23, 10)
        self.assertEqual(year, 2015)
        self.assertEqual(month, 11)
        self.assertEqual(error, False)

    def test_fix_year_month_prev(self):
        """
        Test that it adds to month and subtracts from year to fix date
        when a 'prev' querystring makes month < 12.
        """
        # -6 - 10 = prev querystring of -16
        year, month, error = clean_year_month(2014, -6, 10)
        self.assertEqual(year, 2013)
        self.assertEqual(month, 6)
        self.assertEqual(error, False)

    def test_invalid_month_orig(self):
        """Test that an invalid month in the url returns current
        month and error."""
        year, month, error = clean_year_month(2014, 3, 13)
        self.assertEqual(year, 2014)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(error, ERROR)

    def test_invalid_out_of_bounds_year(self):
        """Test that a next or prev qs that puts the year out of bounds
        returns an error."""
        year, month, error = clean_year_month(2014, 100000, 1)
        self.assertEqual(year, now.year)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(error, ERROR)


class CleanYearMonthDayTest(TestCase):
    """Tests the clean_year_month_day() utility function"""
    def test_valid_next(self):
        year, month, day, error = clean_year_month_day(2014, 3, 31, 1)
        self.assertEqual(year, 2014)
        self.assertEqual(month, 4)
        self.assertEqual(day, 1)
        self.assertEqual(error, False)

    def test_valid_prev(self):
        year, month, day, error = clean_year_month_day(2014, 3, 1, -1)
        self.assertEqual(year, 2014)
        self.assertEqual(month, 2)
        self.assertEqual(day, 28)
        self.assertEqual(error, False)

    def test_invalid_day(self):
        year, month, day, error = clean_year_month_day(2014, 3, 32, 0)
        self.assertEqual(day, 1)
        self.assertEqual(error, ERROR)

    def test_invalid_month(self):
        year, month, day, error = clean_year_month_day(2014, 30, 3, 0)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(error, ERROR)

    def test_invalid_day_and_month(self):
        year, month, day, error = clean_year_month_day(2014, 30, 35, 0)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(day, 1)
        self.assertEqual(error, ERROR)

    def test_invalid_day_and_month_with_net(self):
        year, month, day, error = clean_year_month_day(2014, 30, 35, 1)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(day, 1)
        self.assertEqual(error, ERROR)

    def test_invalid_day_month_and_year(self):
        year, month, day, error = clean_year_month_day(2044, 30, 35, 1)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(day, 1)
        self.assertEqual(error, ERROR)

    def test_invalid_year(self):
        year, month, day, error = clean_year_month_day(2244, 3, 3, 0)
        self.assertEqual(day, 3)
        self.assertEqual(month, timezone.localtime(timezone.now()).month)
        self.assertEqual(year, timezone.localtime(timezone.now()).year)
        self.assertEqual(error, ERROR)

    def test_invalid_beginning_of_year(self):
        """Test valid 'next' querystring at the end of the year"""
        year, month, day, error = clean_year_month_day(2014, 12, 31, 1)
        self.assertEqual(year, 2015)
        self.assertEqual(month, 1)
        self.assertEqual(day, 1)
        self.assertEqual(error, False)
