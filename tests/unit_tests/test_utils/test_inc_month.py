from __future__ import unicode_literals

from django.test import TestCase

from happenings.utils.common import inc_month, dec_month


class IncrementMonthTest(TestCase):
    def test_increment_month(self):
        month, year = inc_month(4, 2014)
        self.assertEqual(month, 5)
        self.assertEqual(year, 2014)

    def test_increment_month_and_year(self):
        month, year = inc_month(12, 2014)
        self.assertEqual(month, 1)
        self.assertEqual(year, 2015)


class DecrementMonthTest(TestCase):
    def test_decrement_month(self):
        year, month = dec_month(2014, 4)
        self.assertEqual(month, 3)
        self.assertEqual(year, 2014)

    def test_increment_month_and_year(self):
        year, month = dec_month(2014, 1)
        self.assertEqual(month, 12)
        self.assertEqual(year, 2013)

    def test_decrement_month_out_of_range(self):
        year, month = dec_month(2014, 4, num=12)
        self.assertEqual(month, 4)
        self.assertEqual(year, 2014)
