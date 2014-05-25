from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.utils.timezone import make_aware, utc
from django.test.utils import override_settings

from happenings.utils.repeater import upcoming_events
from .event_factory import create_event, SetMeUp


@override_settings(TIME_ZONE='UTC')
class UpcomingEventsTest(SetMeUp):
    def test_yearly(self):
        """
        Test yearly repeat w/ 'now' month same as event.start_date.month, and
        day b4 event.start_date.day.
        """
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 3), utc)
        fin = d + timedelta(days=2000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 3, 31))
        self.assertEqual(events[1][0].date(), date(2015, 3, 31))
        self.assertEqual(events[2][0].date(), date(2016, 3, 31))

    def test_yearly2(self):
        """
        Test yearly repeat w/ 'now' month same as event.start_date.month, and
        day after event.start_date.day.
        """
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2015, 3, 3), utc)
        fin = d + timedelta(days=4000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2016, 3, 1))
        self.assertEqual(events[1][0].date(), date(2017, 3, 1))
        self.assertEqual(events[2][0].date(), date(2018, 3, 1))

    def test_yearly3(self):
        """Test yearly repeat w/ 'now' month b4 event.start_date.month."""
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2015, 1, 1), utc)
        fin = d + timedelta(days=4000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2015, 3, 1))
        self.assertEqual(events[1][0].date(), date(2016, 3, 1))
        self.assertEqual(events[2][0].date(), date(2017, 3, 1))

    def test_yearly4(self):
        """Test yearly repeat w/ 'now' month after event.start_date.month."""
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2015, 4, 4), utc)
        fin = d + timedelta(days=4000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2016, 3, 1))
        self.assertEqual(events[1][0].date(), date(2017, 3, 1))
        self.assertEqual(events[2][0].date(), date(2018, 3, 1))

    def test_yearly_future_event(self):
        """Test yearly repeat w/ event that hasn't started yet."""
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2013, 1, 1), utc)
        fin = d + timedelta(days=4000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 3, 1))
        self.assertEqual(events[1][0].date(), date(2015, 3, 1))
        self.assertEqual(events[2][0].date(), date(2016, 3, 1))

    def test_yearly_on_leap_day(self):
        """
        Test yearly repeat event w/ start day on leap day.
        """
        event = create_event(
            start_date=(2012, 2, 29),
            end_date=(2012, 2, 29),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="YEARLY",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 3), utc)
        fin = d + timedelta(days=4000)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 3)
        for i in range(1):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2016, 2, 29))
        self.assertEqual(events[1][0].date(), date(2020, 2, 29))
        self.assertEqual(events[2][0].date(), date(2024, 2, 29))

    def test_monthly(self):
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            utc=True
        )
        d = make_aware(datetime(2014, 6, 6), utc)
        fin = d + timedelta(days=365)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 7, 31))
        self.assertEqual(events[1][0].date(), date(2014, 8, 31))
        self.assertEqual(events[2][0].date(), date(2014, 10, 31))

    def test_monthly2(self):
        """Test with monthly repeating event that started last year."""
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            utc=True
        )
        d = make_aware(datetime(2015, 4, 6), utc)
        fin = d + timedelta(days=365)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2015, 5, 1))
        self.assertEqual(events[1][0].date(), date(2015, 6, 1))
        self.assertEqual(events[2][0].date(), date(2015, 7, 1))

    def test_monthly_with_end_repeat(self):
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Mondo",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2014, 5, 31),
            utc=True
        )
        d = make_aware(datetime(2014, 3, 3), utc)
        fin = d + timedelta(days=365)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 2)

    def test_monthly_future_event(self):
        event = create_event(
            start_date=(2015, 3, 10),
            end_date=(2015, 3, 10),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            utc=True
        )
        d = make_aware(datetime(2015, 1, 6), utc)
        fin = d + timedelta(days=365)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0][0].date(), date(2015, 3, 10))

    def test_weekly(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 3),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 6), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 3, 8))
        self.assertEqual(events[1][0].date(), date(2014, 3, 15))

    def test_weekly_future_event(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 3),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            utc=True
        )
        d = make_aware(datetime(2013, 12, 1), utc)
        fin = d + timedelta(days=900)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0][0].date(), date(2014, 3, 1))
        self.assertEqual(events[1][0].date(), date(2014, 3, 8))
        self.assertEqual(events[2][0].date(), date(2014, 3, 15))

    def test_biweekly(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 3),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="BIWEEKLY",
            utc=True
        )
        d = make_aware(datetime(2014, 5, 8), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 5, 10))
        self.assertEqual(events[1][0].date(), date(2014, 5, 24))

    def test_daily(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="DAILY",
            utc=True
        )
        d = make_aware(datetime(2014, 5, 6), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 5, 6))
        self.assertEqual(events[1][0].date(), date(2014, 5, 7))

    def test_daily_future_event(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="DAILY",
            utc=True
        )
        d = make_aware(datetime(2013, 11, 6), utc)
        fin = d + timedelta(days=900)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        self.assertEqual(events[0][0].date(), date(2014, 3, 1))
        self.assertEqual(events[1][0].date(), date(2014, 3, 2))

    def test_weekday_start_on_weekend(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        d = make_aware(datetime(2014, 5, 3), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 5, 5))
        self.assertEqual(events[1][0].date(), date(2014, 5, 6))

    def test_weekday_start_on_weekday(self):
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 1),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        d = make_aware(datetime(2014, 5, 7), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 5, 7))
        self.assertEqual(events[1][0].date(), date(2014, 5, 8))
        self.assertEqual(events[2][0].date(), date(2014, 5, 9))
        self.assertEqual(events[3][0].date(), date(2014, 5, 12))
        self.assertEqual(events[4][0].date(), date(2014, 5, 13))

    def test_weekday_with_end_repeat(self):
        event = create_event(
            start_date=(2014, 3, 31),
            end_date=(2014, 3, 31),
            created_by=self.user,
            title="Groove",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            end_repeat=date(2014, 4, 1),
            utc=True
        )
        d = make_aware(datetime(2014, 3, 3), utc)
        fin = d + timedelta(days=365)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 2)

    def test_weekday_event_in_future(self):
        event = create_event(
            start_date=(2014, 3, 10),
            end_date=(2014, 3, 10),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        d = make_aware(datetime(2014, 2, 7), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 5)
        for i in range(5):
            self.assertEqual(events[i][1].title, event.title)
            self.assertEqual(events[i][1].start_date, event.start_date)
        self.assertEqual(events[0][0].date(), date(2014, 3, 10))

    def test_single_day_event_in_future(self):
        event = create_event(
            start_date=(2014, 3, 7),
            end_date=(2014, 3, 7),
            created_by=self.user,
            title="Vera",
            description="Testing 1 2 3",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 3), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0], event.start_date)
        self.assertEqual(events[0][1].title, event.title)
        self.assertEqual(events[0][1].start_date, event.start_date)

    def test_event_in_past(self):
        """
        Sending an event that has already started and ended, and that
        doesn't have an end repeat, should return an empty list.
        """
        event = create_event(
            start_date=(2014, 3, 7),
            end_date=(2014, 3, 7),
            created_by=self.user,
            title="Elvira",
            description="Testing 1 2 3",
            utc=True
        )
        d = make_aware(datetime(2015, 3, 4), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_end_repeat(self):
        """Test that an event's end_repeat is respected."""
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 3),
            created_by=self.user,
            title="Veronika",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2014, 3, 10),
            utc=True
        )
        d = make_aware(datetime(2014, 3, 6), utc)
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0].date(), date(2014, 3, 8))
        self.assertEqual(events[0][1].title, event.title)

    def test_event_starts_outside_of_bound(self):
        """
        Passing an event that starts outside of 'finish' argument
        should return an empty list.
        """
        event = create_event(
            start_date=(2015, 3, 1),
            end_date=(2015, 3, 3),
            created_by=self.user,
            title="Veronica",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 6), utc)
        # set finish arg to 90 days from d
        fin = d + timedelta(days=90)
        events = upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_different_num(self):
        """
        If the 'num' argument is supplied, should return 'num' number of
        events.
        """
        num = 8
        event = create_event(
            start_date=(2014, 3, 1),
            end_date=(2014, 3, 3),
            created_by=self.user,
            title="Veronica",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            utc=True
        )
        d = make_aware(datetime(2014, 3, 6), utc)
        fin = d + timedelta(days=900)
        events = upcoming_events(event, d, fin, num)
        self.assertEqual(len(events), 8)
