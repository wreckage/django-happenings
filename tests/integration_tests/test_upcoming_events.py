from __future__ import unicode_literals

from datetime import datetime, date, timedelta

from django.utils.timezone import make_aware, utc
from django.test.utils import override_settings

from happenings.utils.upcoming import UpcomingEvents
from happenings.templatetags.happenings_tags import current_happenings as haps
from .event_factory import create_event, SetMeUp


@override_settings(TIME_ZONE='UTC')
class UpcomingEventsTest(SetMeUp):
    def upcoming_events(self, event, d, fin, num=5):
        return UpcomingEvents(event, d, fin, num).get_upcoming_events()

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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin)
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
        events = self.upcoming_events(event, d, fin, num)
        self.assertEqual(len(events), num)

    def test_events_over_for_day_weekday(self):
        """
        Tests that an event that is over for the day doesn't show up,
        but that an even not over for the day, does.
        """
        event = create_event(
            start_date=(2014, 3, 1, 21),
            end_date=(2014, 3, 1, 22),
            created_by=self.user,
            title="Jill",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            end_repeat=date(2014, 3, 10),
            utc=True
        )
        d = make_aware(datetime(2014, 3, 6, 20), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][0].date(), date(2014, 3, 6))
        self.assertEqual(events[0][1].title, event.title)
        d = make_aware(datetime(2014, 3, 6, 23), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_events_over_for_day_monthly(self):
        """
        Tests that an event that is over for the day doesn't show up,
        but that an even not over for the day, does.
        """
        event = create_event(
            start_date=(2015, 5, 1, 21),
            end_date=(2015, 5, 1, 22),
            created_by=self.user,
            title="Albert",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 1, 20), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        d = make_aware(datetime(2015, 5, 1, 23), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_events_over_for_day_yearly(self):
        """
        Tests that an event that is over for the day doesn't show up,
        but that an even not over for the day, does.
        """
        event = create_event(
            start_date=(2015, 5, 1, 21),
            end_date=(2015, 5, 1, 22),
            created_by=self.user,
            title="Chelsea",
            description="Testing 1 2 3",
            repeat="YEARLY",
            end_repeat=date(2017, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 1, 20), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        d = make_aware(datetime(2015, 5, 1, 23), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_events_over_for_day_weekly(self):
        """
        Tests that an event that is over for the day doesn't show up,
        but that an even not over for the day, does.
        """
        event = create_event(
            start_date=(2015, 5, 1, 21),
            end_date=(2015, 5, 1, 22),
            created_by=self.user,
            title="Leon",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 8, 20), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        d = make_aware(datetime(2015, 5, 8, 23), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_events_over_for_day_daily(self):
        """
        Tests that an event that is over for the day doesn't show up,
        but that an even not over for the day, does.
        """
        event = create_event(
            start_date=(2015, 5, 1, 21),
            end_date=(2015, 5, 1, 22),
            created_by=self.user,
            title="Leon",
            description="Testing 1 2 3",
            repeat="DAILY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 6, 20), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)
        d = make_aware(datetime(2015, 5, 6, 23), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)

    def test_multiday_event_weekly_repeat(self):
        """
        Tests that a multiday event (hitherto called an event 'chunk') doesn't
        show up in upcoming events if the event already 'started'
        """
        event = create_event(
            start_date=(2015, 5, 19),
            end_date=(2015, 5, 21),
            created_by=self.user,
            title="Ada",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 27), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)
        d = make_aware(datetime(2015, 5, 26), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)

    def test_multiday_event_biweekly_repeat(self):
        """
        Tests that a multiday event (hitherto called an event 'chunk') doesn't
        show up in upcoming events if the event already 'started'
        """
        event = create_event(
            start_date=(2015, 5, 1),
            end_date=(2015, 5, 2),
            created_by=self.user,
            title="Claire",
            description="Testing 1 2 3",
            repeat="BIWEEKLY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        d = make_aware(datetime(2015, 5, 16), utc)
        fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 0)
        d = make_aware(datetime(2015, 5, 15), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)

    def test_multiday_event_monthly_repeat(self):
        """
        Tests that a multiday event (hitherto called an event 'chunk') doesn't
        show up in upcoming events if the event already 'started'
        """
        event = create_event(
            start_date=(2015, 5, 1),
            end_date=(2015, 5, 3),
            created_by=self.user,
            title="Chris",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2015, 8, 10),
            utc=True
        )
        for day in (2, 3):
            d = make_aware(datetime(2015, 6, day), utc)
            fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
            events = self.upcoming_events(event, d, fin)
            self.assertEqual(len(events), 0)
        d = make_aware(datetime(2015, 6, 1), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)

    def test_multiday_event_yearly_repeat(self):
        """
        Tests that a multiday event (hitherto called an event 'chunk') doesn't
        show up in upcoming events if the event already 'started'
        """
        event = create_event(
            start_date=(2015, 5, 1),
            end_date=(2015, 5, 3),
            created_by=self.user,
            title="Barry",
            description="Testing 1 2 3",
            repeat="YEARLY",
            end_repeat=date(2018, 8, 10),
            utc=True
        )
        for day in (2, 3):
            d = make_aware(datetime(2016, 5, day), utc)
            fin = d.replace(hour=23, minute=59, second=59, microsecond=999)
            events = self.upcoming_events(event, d, fin)
            self.assertEqual(len(events), 0)
        d = make_aware(datetime(2016, 5, 1), utc)
        events = self.upcoming_events(event, d, fin)
        self.assertEqual(len(events), 1)

# ------------------------Current Happenings Test -------------------------- #
# Kept getting invocation error when trying to create a new file for these
# tests so I'm putting them here for now

    def hap(self, event, d):
        # need to know the length of the returned generator, so used a little
        # hack found here: http://stackoverflow.com/a/7223557/3188521
        return sum(1 for _ in haps(now=d)['events_happening_now'])

    def test_hap_no_repeat(self):
        event = create_event(
            start_date=(2015, 6, 14, 20),
            end_date=(2015, 6, 14, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            utc=True
        )
        for hr in (20, 21, 22):
            d = make_aware(datetime(2015, 6, 14, hr), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
        for hr in (19, 23):
            d = make_aware(datetime(2015, 6, 14, hr), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 0)

    def test_hap_weekly_repeat(self):
        event = create_event(
            start_date=(2015, 6, 14, 20),
            end_date=(2015, 6, 14, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2015, 6, 23),
            utc=True
        )
        d = make_aware(datetime(2015, 6, 14, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 14, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 14, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 21, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 21, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 21, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 21, 19), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 21, 22), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 21, 18), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 14, 19), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 14, 22), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 14, 18), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 28, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 28, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 28, 21, 44), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_biweekly_repeat(self):
        event = create_event(
            start_date=(2015, 6, 1, 20),
            end_date=(2015, 6, 1, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="BIWEEKLY",
            end_repeat=date(2015, 6, 16),
            utc=True
        )
        d = make_aware(datetime(2015, 6, 1, 21), utc)
        events = self.hap(event, d)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 1, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 1, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 8, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 8, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 8, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 15, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 15, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 15, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 29, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 29, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 29, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_weekday_repeat(self):
        event = create_event(
            start_date=(2015, 6, 1, 20),
            end_date=(2015, 6, 1, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            end_repeat=date(2015, 6, 16),
            utc=True
        )
        d = make_aware(datetime(2015, 6, 1, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 1, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 1, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 7, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 7, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 7, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 8, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 8, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 8, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        # not happening
        d = make_aware(datetime(2015, 6, 1, 19), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 1, 23), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 1, 22, 2), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        # check that end_repeat is respected
        d = make_aware(datetime(2015, 6, 17, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 17, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 17, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_weekday_repeat_future(self):
        event = create_event(
            start_date=(2016, 6, 1, 20),
            end_date=(2016, 6, 1, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="WEEKDAY",
            utc=True
        )
        d = make_aware(datetime(2015, 6, 1, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 1, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 1, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_monthly_repeat(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 2, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2015, 8, 1),
            utc=True
        )
        d = make_aware(datetime(2015, 6, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 3, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 3, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 3, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 7, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 7, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 7, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        # make sure end_repeat is respected
        d = make_aware(datetime(2015, 9, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 9, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 9, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        # test prev. year
        d = make_aware(datetime(2014, 6, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2014, 6, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2014, 6, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_yearly_repeat(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 2, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="YEARLY",
            end_repeat=date(2017, 8, 1),
            utc=True
        )
        d = make_aware(datetime(2015, 6, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2015, 6, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

        d = make_aware(datetime(2015, 6, 3, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 3, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 3, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 2, 19), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 2, 22, 2), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

        d = make_aware(datetime(2016, 6, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2016, 6, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)
        d = make_aware(datetime(2016, 6, 2, 21, 59), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 1)

    def test_hap_yearly_repeat_multi(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 4, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="YEARLY",
            end_repeat=date(2017, 8, 1),
            utc=True
        )
        for year in (2015, 2016):
            for day in (2, 3, 4):
                d = make_aware(datetime(year, 6, day, 21), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(year, 6, day, 20), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(year, 6, day, 21, 59), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(year, 6, day, 19), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 0)
                d = make_aware(datetime(year, 6, day, 22, 2), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 7, 2, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 5, 2, 20), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)

    def test_hap_monthly_repeat_multi(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 4, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="MONTHLY",
            end_repeat=date(2017, 8, 1),
            utc=True
        )
        for month in (6, 7):
            for day in (2, 3, 4):
                d = make_aware(datetime(2015, month, day, 21), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(2015, month, day, 20), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(2015, month, day, 21, 59), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 1)
                d = make_aware(datetime(2015, month, day, 19), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 0)
                d = make_aware(datetime(2015, month, day, 22, 2), utc)
                events = self.hap(event, d)
                self.assertEqual(events, 0)

    def test_hap_weekly_repeat_multi(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 4, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="WEEKLY",
            end_repeat=date(2017, 8, 1),
            utc=True
        )
        for day in (2, 3, 4, 9, 10, 11):
            d = make_aware(datetime(2015, 6, day, 21), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 20), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 21, 59), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 19), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 0)
            d = make_aware(datetime(2015, 6, day, 22, 2), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 0)

    def test_hap_no_repeat_multi(self):
        event = create_event(
            start_date=(2015, 6, 2, 20),
            end_date=(2015, 6, 4, 22),
            created_by=self.user,
            title="Happening",
            description="Testing 1 2 3",
            repeat="NEVER",
            end_repeat=date(2017, 8, 1),
            utc=True
        )
        for day in (2, 3, 4):
            d = make_aware(datetime(2015, 6, day, 21), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 20), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 21, 59), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 1)
            d = make_aware(datetime(2015, 6, day, 19), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 0)
            d = make_aware(datetime(2015, 6, day, 22, 2), utc)
            events = self.hap(event, d)
            self.assertEqual(events, 0)

        d = make_aware(datetime(2015, 6, 1, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
        d = make_aware(datetime(2015, 6, 5, 21), utc)
        events = self.hap(event, d)
        self.assertEqual(events, 0)
