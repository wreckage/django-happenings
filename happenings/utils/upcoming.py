# Used to generate upcoming events

from __future__ import unicode_literals

from datetime import timedelta, date, datetime

from django.utils.timezone import make_aware, get_default_timezone
from django.utils.six.moves import xrange

from happenings.utils.common import inc_month


class UpcomingEvents(object):
    def __init__(self, event, now, finish, num=5):
        self.event = event
        self.finish = finish  # datetime.datetime
        self.now = now        # datetime.datetime
        self.num = num
        self.events = []

    def get_upcoming_events(self):
        """
        Repeats an event and returns 'num' (or fewer)
        upcoming events from 'now'.
        """
        if self.event.repeats('NEVER'):
            has_ended = False
            now_gt_start = self.now > self.event.l_start_date
            now_gt_end = self.now > self.event.end_date
            if now_gt_end or now_gt_start:
                has_ended = True
            has_not_started = self.event.l_start_date > self.finish
            if has_ended or has_not_started:
                return self.events
            self.events.append((self.event.l_start_date, self.event))
            return self.events
        if self.event.repeats('WEEKDAY'):
            self._weekday()
        elif self.event.repeats('MONTHLY'):
            self._monthly()
        elif self.event.repeats('YEARLY'):
            self._yearly()
        else:
            self._others()
        return self.events

    def we_should_stop(self, start, start_):
        """
        Checks 'start' to see if we should stop collecting upcoming events.
        'start' should be a datetime.datetime, 'start_' should be the same
        as 'start', but it should be a datetime.date to allow comparison
        w/ end_repeat.
        """
        if start > self.finish or \
                self.event.end_repeat is not None and \
                start_ > self.event.end_repeat:
            return True
        else:
            return False

    def _yearly(self):
        num = self.num
        year = self.now.year
        if self.event.l_start_date > self.now:  # event starts in the future
            year = self.event.l_start_date.year
        elif self.now.month > self.event.l_start_date.month:
            year += 1
        # The event occurs this month, so check the day to see if passed
        elif self.now.month == self.event.l_start_date.month:
            # if the current day is > event day, or if the event was today but
            # finished, increment the year.
            if self.now.day > self.event.l_start_date.day or \
                self.now.day == self.event.l_start_date.day and \
                    self.now.time() > self.event.l_start_date.time():
                year += 1
        month = self.event.l_start_date.month
        day = self.event.l_start_date.day
        while num:
            try:
                start = make_aware(
                    datetime(year, month, day), get_default_timezone()
                )
                # change to date() so we can compare to event.end_repeat
                start_ = date(year, month, day)
            # value error most likely means that the event's start date doesn't
            # appear this calendar month
            except ValueError:
                year += 1
                continue
            if self.we_should_stop(start, start_):
                return
            self.events.append((start, self.event))
            year += 1
            num -= 1

    def _monthly(self):
        num = self.num
        start = self.event.l_start_date
        year = self.now.year
        month = self.now.month
        day = self.event.l_start_date.day
        if self.event.l_start_date > self.now:  # event starts in the future
            year = self.event.l_start_date.year
            month = self.event.l_start_date.month
        while num:
            try:
                start = start.replace(year=year, month=month)
                if self.now > start:  # if event already happened
                    month, year = inc_month(month, year)
                    continue
                # change to date() so we can compare to event.end_repeat
                start_ = date(year, month, day)
            # value error most likely means that the event's start date doesn't
            # appear this calendar month
            except ValueError:
                month, year = inc_month(month, year)
                continue
            if self.we_should_stop(start, start_):
                return
            self.events.append((start, self.event))
            month, year = inc_month(month, year)
            num -= 1

    def _weekday(self):
        start = self.event.l_start_date
        if not self.event.l_start_date > self.now:
            start = start.replace(
                year=self.now.year, month=self.now.month, day=self.now.day
            )
        while start.weekday() > 4:
            start += timedelta(days=1)
        if start < self.now:
            start += timedelta(days=1)
            while start.weekday() > 4:
                start += timedelta(days=1)
        for i in xrange(self.num):
            # change to date() so we can compare to event.end_repeat
            start_ = date(start.year, start.month, start.day)
            if self.we_should_stop(start, start_):
                return
            while start.weekday() > 4:
                start += timedelta(days=1)
            self.events.append((start, self.event))
            start += timedelta(days=1)

    def _others(self):
        repeat = {'WEEKLY': 7, 'BIWEEKLY': 14, 'DAILY': 1}
        if self.event.repeats('DAILY'):
            if self.event.l_start_date > self.now:
                start = self.event.l_start_date
            elif self.event.l_start_date.time() < self.now.time():
                # has it already begun? Then no longer upcoming, so ++day
                start = self.now
                start += timedelta(days=1)
            else:
                start = self.now
        else:
            start = self.event.l_start_date
            end = self.event.l_end_date
            while start < self.now or end <= self.now:
                start += timedelta(days=repeat[self.event.repeat])
                end += timedelta(days=repeat[self.event.repeat])
        for i in xrange(self.num):
            # change to date() so we can compare to event.end_repeat
            start_ = date(start.year, start.month, start.day)
            if self.we_should_stop(start, start_):
                return
            self.events.append((start, self.event))
            start += timedelta(days=repeat[self.event.repeat])
