from __future__ import unicode_literals

import datetime

from happenings.models import Event
from .event_factory import create_event, SetMeUp
from happenings.utils.next_event import get_next_event


class NextEventTest(SetMeUp):
    def test_next_event_single(self):
        """Test a non-chunk event"""
        create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKLY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2014, 3, 5)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 8))

        date = datetime.datetime(2014, 4, 9)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 4, 12))

    def test_next_event_start_end_diff_month(self):
        create_event(
            start_date=(2014, 2, 28),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKLY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2014, 3, 1)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 1))

    def test_next_event_start_end_diff_month_monthly_repeat(self):
        create_event(
            start_date=(2014, 2, 28),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="MONTHLY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2014, 3, 1)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 1))

        date = datetime.datetime(2014, 5, 5)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 5, 28))

    def test_next_event_weekly_repeat(self):
        create_event(
            start_date=(2014, 2, 15),
            end_date=(2014, 2, 16),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKLY",
        )
        event = Event.objects.all()
        # use date_dicts, and put the for loop into its own func (like i did
        # with check_dates)
        # date_dicts = [
        #    {datetime.datetime(2014, 2, 19): (2014, 2, 22)},
        #    {datetime.datetime(2014, 3, 13): (2014, 3, 15)},
        #    {datetime.datetime(2014, 4, 5): (2014, 4, 5)},
        #    {datetime.datetime(2015, 4, 5): (2015, 4, 5)}
        # ]

        # for date_dict in date_dicts:
        #    for d in date_dict.items():
        #        z, x = d[0], d[1]
        #        y, m, d = get_next_event(event, z)
        #        self.assertEqual((y, m, d), x)

        date = datetime.datetime(2014, 2, 19)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 2, 22))

        date = datetime.datetime(2014, 3, 13)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 15))

        date = datetime.datetime(2014, 4, 5)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 4, 5))

        date = datetime.datetime(2015, 4, 5)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 4, 5))

    def test_next_event_biweekly_repeat(self):
        create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 4),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="BIWEEKLY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2014, 3, 13)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 15))

        date = datetime.datetime(2014, 4, 12)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 4, 12))

        date = datetime.datetime(2014, 3, 1)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 3, 1))

    def test_next_event_monthly_repeat(self):
        create_event(
            start_date=(2014, 4, 1),
            end_date=(2014, 4, 3),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="MONTHLY",
        )
        event = Event.objects.all()

        dates = [
            [(2014, 4, 7), (2014, 5, 1)],
            [(2014, 5, 20), (2014, 6, 1)],
            [(2014, 6, 2), (2014, 6, 2)],
            [(2014, 4, 3), (2014, 4, 3)],
            [(2014, 4, 4), (2014, 5, 1)],
            [(2014, 2, 2), (2014, 4, 1)],
        ]
        for item in dates:
            now = datetime.datetime(*item[0])
            y, m, d = get_next_event(event, now)
            self.assertEqual((y, m, d), item[1])

    def test_next_event_yearly_repeat(self):
        create_event(
            start_date=(2014, 5, 3),
            end_date=(2014, 5, 6),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="YEARLY",
        )
        event = Event.objects.all()

        dates = [
            [(2014, 4, 7), (2014, 5, 3)],
            [(2014, 5, 1), (2014, 5, 3)],
            [(2014, 5, 7), (2015, 5, 3)],
            [(2015, 1, 7), (2015, 5, 3)],
            [(2017, 5, 5), (2017, 5, 5)],
        ]
        for item in dates:
            now = datetime.datetime(*item[0])
            y, m, d = get_next_event(event, now)
            self.assertEqual((y, m, d), item[1])

    def test_next_event_weekday_repeat_starts_on_non_weekday(self):
        create_event(
            start_date=(2014, 6, 1),
            end_date=(2014, 6, 1),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKDAY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2014, 5, 7)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 6, 2))

    def test_next_event_bugfix(self):
        """
        This tests a bug that was discovered on May 28, 2014 that
        had the wrong next event being shown.
        """
        create_event(
            start_date=(2014, 5, 26),
            end_date=(2014, 5, 26),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKLY",
        )
        event = Event.objects.all()
        date = datetime.datetime(2014, 5, 29)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2014, 6, 2))

    def test_next_event_bugfix2(self):
        """
        This tests a bug that was discovered on June 6, 2014 that
        had the wrong next event being shown for a yearly repeating event.
        """
        create_event(
            start_date=(2014, 3, 15),
            end_date=(2014, 3, 15),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="YEARLY",
        )
        event = Event.objects.all()
        date = datetime.datetime(2014, 6, 6)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 3, 15))

    def test_next_event_over_same_day(self):
        """Test that an event over for the day doesn't show up."""
        create_event(
            start_date=(2015, 5, 1, 10),
            end_date=(2015, 5, 1, 13),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKDAY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2015, 5, 4, 9)  # before
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 4))
        date = date.replace(hour=12)  # during
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 5))
        date = date.replace(hour=14)  # after
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 5))

    def test_next_event_with_time(self):
        """
        Test that an event over for today, but not scheduled to
        even appear for today, shows up correctly.
        """
        create_event(
            start_date=(2015, 5, 22, 10),
            end_date=(2015, 5, 22, 13),
            created_by=self.user,
            title="The Event",
            description="This is an event. Enjoy.",
            repeat="WEEKLY",
        )
        event = Event.objects.all()

        date = datetime.datetime(2015, 5, 28, 9)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 29))
        date = date.replace(hour=12)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 29))
        date = date.replace(hour=14)
        y, m, d = get_next_event(event, date)
        self.assertEqual((y, m, d), (2015, 5, 29))
