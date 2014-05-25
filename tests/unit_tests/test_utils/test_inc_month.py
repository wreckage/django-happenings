from __future__ import unicode_literals

from django.test import TestCase

from happenings.utils.common import inc_month


class IncrementMonthTest(TestCase):
    def test_increment_month(self):
        month, year = inc_month(4, 2014)
        self.assertEqual(month, 5)
        self.assertEqual(year, 2014)

    def test_increment_month_and_year(self):
        month, year = inc_month(12, 2014)
        self.assertEqual(month, 1)
        self.assertEqual(year, 2015)
