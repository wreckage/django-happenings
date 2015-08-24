from __future__ import unicode_literals

from collections import defaultdict
from datetime import date, timedelta

from django.utils.six.moves import xrange


class Repeater(object):
    def __init__(self, count, year, month, day=None, end_repeat=None,
                 event=None, num=7, count_first=False, end_on=None):
        self.count = count  # defaultdict(list)
        self.year = year
        self.month = month
        self.day = day
        self.end_repeat = end_repeat  # datetime.date()
        self.event = event  # Event object
        self.num = num
        self.count_first = count_first
        self.end_on = end_on
        if end_repeat is None:  # set to far off date to simulate 'forever'
            self.end_repeat = date(2200, 3, 3)

    def count_it(self, day):
        self.count[day].append((self.event.title, self.event.pk))

    def repeat(self, day=None):
        """
        Add 'num' to the day and count that day until we reach end_repeat, or
        until we're outside of the current month, counting the days
        as we go along.
        """
        if day is None:
            day = self.day

        try:
            d = date(self.year, self.month, day)
        except ValueError:  # out of range day
            return self.count

        if self.count_first and d <= self.end_repeat:
            self.count_it(d.day)

        d += timedelta(days=self.num)

        if self.end_on is not None:
            while d.month == self.month and \
                    d <= self.end_repeat and \
                    d.day <= self.end_on:
                self.count_it(d.day)
                d += timedelta(days=self.num)
        else:
            while d.month == self.month and d <= self.end_repeat:
                self.count_it(d.day)
                d += timedelta(days=self.num)

    def repeat_weekdays(self):
        """
        Like self.repeat(), but used to repeat every weekday.
        """
        try:
            d = date(self.year, self.month, self.day)
        except ValueError:  # out of range day
            return self.count

        if self.count_first and \
                d <= self.end_repeat and \
                d.weekday() not in (5, 6):
            self.count_it(d.day)

        d += timedelta(days=1)

        while d.month == self.month and d <= self.end_repeat:
            if d.weekday() not in (5, 6):
                self.count_it(d.day)
            d += timedelta(days=1)

    def repeat_reverse(self, start, end):
        """
        Starts from 'start' day and counts backwards until 'end' day.
        'start' should be >= 'end'. If it's equal to, does nothing.
        If a day falls outside of end_repeat, it won't be counted.
        """
        day = start
        diff = start - end
        try:
            if date(self.year, self.month, day) <= self.end_repeat:
                self.count_it(day)
        # a value error likely means the event runs past the end of the month,
        # like an event that ends on the 31st, but the month doesn't have that
        # many days. Ignore it b/c the dates won't be added to calendar anyway
        except ValueError:
            pass
        for i in xrange(diff):
            day -= 1
            try:
                if date(self.year, self.month, day) <= self.end_repeat:
                    self.count_it(day)
            except ValueError:
                pass

    def repeat_chunk(self, diff):
        for i in xrange(diff):
            self.repeat(self.day + i + 1)

    def repeat_biweekly(self):
        """
        This function is unique b/c it creates an empty defaultdict,
        adds in the event occurrences by creating an instance of Repeater,
        then returns the defaultdict, likely to be merged into the 'main'
        defaultdict (the one holding all event occurrences for this month).
        """
        mycount = defaultdict(list)
        d = self.event.l_start_date
        while d.year != self.year or d.month != self.month:
            d += timedelta(days=14)
        r = self.__class__(
            mycount, self.year, self.month, d.day, self.event.end_repeat,
            self.event, num=self.num, count_first=True
        )
        r.repeat()
        if self.event.is_chunk() and r.count:
            r.day = min(r.count)
            r.repeat_chunk(self.event.start_end_diff)
        return r.count


class YearlyRepeater(Repeater):
    def _repeat_chunk(self):
        self.day = self.event.l_start_date.day
        self.num = 1
        if self.event.end_repeat is not None:
            self.end_repeat = self.event.end_repeat

        if self.event.l_start_date.month == self.month:
            if self.event.starts_ends_same_month():
                self.end_on = self.event.l_end_date.day
            self.repeat()
        elif (self.event.l_end_date.month == self.month
              and not self.event.starts_ends_same_month()):
            self.repeat_reverse(self.event.l_end_date.day, 1)

    def repeat_it(self):
        """
        Events that repeat every year should be shown every year
        on the same date they started e.g. an event that starts on March 23rd
        would appear on March 23rd every year it is scheduled to repeat.
        If the event is a chunk event, hand it over to _repeat_chunk().
        """
        # The start day will be counted if we're in the start year,
        # so only count the day if we're in the same month as
        # l_start_date, but not in the same year.
        if self.event.l_start_date.month == self.month and \
                self.event.l_start_date.year != self.year:
            self.count_it(self.event.l_start_date.day)
        # If we're in the same mo & yr as l_start_date,
        # should already be filled in
        if self.event.is_chunk() and not \
                self.event.starts_same_year_month_as(self.year, self.month):
            self._repeat_chunk()
        return self.count


class MonthlyRepeater(Repeater):
    def _repeat_chunk(self):
        start_day = self.event.l_start_date.day
        last_day_last_mo = date(self.year, self.month, 1) - timedelta(days=1)

        self.day = start_day
        self.num = 1
        if self.event.end_repeat is not None:
            self.end_repeat = self.event.end_repeat

        if not self.event.starts_same_year_month_as(self.year, self.month):
            if not self.event.starts_ends_same_month():
                    self.repeat()  # fill out the end of the month
                    # fill out the beginning of the month, if nec.
                    if start_day <= last_day_last_mo.day:
                        self.repeat_reverse(
                            self.event.l_end_date.day, 1
                        )
            else:
                self.repeat_reverse(
                    self.event.l_end_date.day, start_day + 1
                )

    def repeat_it(self):
        """
        Events that repeat every month should be shown every month
        on the same date they started e.g. an event that starts on the 23rd
        would appear on the 23rd every month it is scheduled to repeat.
        """
        start_day = self.event.l_start_date.day
        if not self.event.starts_same_month_as(self.month):
            self.count_it(start_day)
        elif self.event.starts_same_month_not_year_as(self.month, self.year):
            self.count_it(start_day)

        if self.event.is_chunk():
            self._repeat_chunk()
        return self.count


class DailyRepeater(Repeater):
    """Handles repeating daily and every weekday."""
    def repeat_it(self):
        if self.event.end_repeat is not None:
            self.end_repeat = self.event.end_repeat

        if self.event.starts_same_year_month_as(self.year, self.month):
            # we assume that l_start_date was already counted, so no
            # count_first=True
            self.day = self.event.l_start_date.day
        else:
            # Note count_first=True b/c although the start date isn't this
            # month, the event does begin repeating this month and start_date
            # has not yet been counted.
            self.day = date(self.year, self.month, 1).day
            self.count_first = True

        if self.event.repeats('DAILY'):
            self.num = 1
            self.repeat()
        else:
            self.repeat_weekdays()
        return self.count


class WeeklyRepeater(Repeater):
    def _biweekly_helper(self):
        """Created to take some of the load off of _handle_weekly_repeat_out"""
        self.num = 14
        mycount = self.repeat_biweekly()
        if mycount:
            if self.event.is_chunk() and min(mycount) not in xrange(1, 8):
                mycount = _chunk_fill_out_first_week(
                    self.year, self.month, mycount, self.event,
                    diff=self.event.start_end_diff,
                )
            for k, v in mycount.items():
                for item in v:
                    self.count[k].append(item)

    def _handle_weekly_repeat_out(self):
        """
        Handles repeating an event weekly (or biweekly) if the current
        year and month are outside of its start year and month.
        It takes care of cases 3 and 4 in _handle_weekly_repeat_in() comments.
        """
        start_d = _first_weekday(
            self.event.l_start_date.weekday(), date(self.year, self.month, 1)
        )
        self.day = start_d.day
        self.count_first = True
        if self.event.repeats('BIWEEKLY'):
            self._biweekly_helper()
        elif self.event.repeats('WEEKLY'):
            # Note count_first=True b/c although the start date isn't this
            # month, the event does begin repeating this month and start_date
            # has not yet been counted.
            # Also note we start from start_d.day and not
            # event.l_start_date.day
            self.repeat()
            if self.event.is_chunk():
                diff = self.event.start_end_diff
                self.count = _chunk_fill_out_first_week(
                    self.year, self.month, self.count, self.event, diff
                )
                for i in xrange(diff):
                    # count the chunk days, then repeat them
                    self.day = start_d.day + i + 1
                    self.repeat()

    def _handle_weekly_repeat_in(self):
        """
        Handles repeating both weekly and biweekly events, if the
        current year and month are inside it's l_start_date and l_end_date.
        Four possibilites:
            1. The event starts this month and ends repeating this month.
            2. The event starts this month and doesn't finish repeating
            this month.
            3. The event didn't start this month but ends repeating this month.
            4. The event didn't start this month and doesn't end repeating
            this month.
        """
        self.day = self.event.l_start_date.day
        self.count_first = False
        repeats = {'WEEKLY': 7, 'BIWEEKLY': 14}
        if self.event.starts_same_year_month_as(self.year, self.month):
            # This takes care of 1 and 2 above.
            # Note that 'count' isn't incremented before adding a week (in
            # Repeater.repeat()), b/c it's assumed that l_start_date
            # was already counted.
            for repeat, num in repeats.items():
                self.num = num
                if self.event.repeats(repeat):
                    self.repeat()
                    if self.event.is_chunk():
                        self.repeat_chunk(diff=self.event.start_end_diff)

    def repeat_it(self):
        if self.event.end_repeat is not None:
            self.end_repeat = self.event.end_repeat

        if self.event.starts_same_year_month_as(self.year, self.month):
            self._handle_weekly_repeat_in()
        else:
            self._handle_weekly_repeat_out()
        return self.count


# XXX _first_weekday() and _chunk_fill_out_the_first_week() are currently
# only used in WeeklyRepeat, so maybe move them in there.
def _first_weekday(weekday, d):
    """
    Given a weekday and a date, will increment the date until it's
    weekday matches that of the given weekday, then that date is returned.
    """
    while weekday != d.weekday():
        d += timedelta(days=1)
    return d


def _chunk_fill_out_first_week(year, month, count, event, diff):
    """
    If a repeating chunk event exists in a particular month, but didn't
    start that month, it may be neccessary to fill out the first week.
    Five cases:
        1. event starts repeating on the 1st day of month
        2. event starts repeating past the 1st day of month
        3. event starts repeating before the 1st day of month, and continues
        through it.
        4. event starts repeating before the 1st day of month, and finishes
        repeating before it.
        5. event starts repeating before the 1st day of month, and finishes
        on it.
    """
    first_of_the_month = date(year, month, 1)
    d = _first_weekday(event.l_end_date.weekday(), first_of_the_month)
    d2 = _first_weekday(event.l_start_date.weekday(), first_of_the_month)
    diff_weekdays = d.day - d2.day
    day = first_of_the_month.day
    start = event.l_start_date.weekday()
    first = first_of_the_month.weekday()

    if start == first or diff_weekdays == diff:
        return count
    elif start > first:
        end = event.l_end_date.weekday()
        diff = end - first + 1
    elif start < first:
        diff = d.day
    for i in xrange(diff):
        if event.end_repeat is not None and \
                date(year, month, day) >= event.end_repeat:
            break
        count[day].append((event.title, event.pk))
        day += 1
    return count


class CountHandler(object):
    def __init__(self, year, month, events):
        self.year = year
        self.month = month
        self.events = events
        self.count = defaultdict(list)

    def _handle_single_chunk(self, event):
        """
        This handles either a non-repeating event chunk, or the first
        month of a repeating event chunk.
        """
        if not event.starts_same_month_as(self.month) and not \
                event.repeats('NEVER'):
            # no repeating chunk events if we're not in it's start month
            return

        # add the events into an empty defaultdict. This is better than passing
        # in self.count, which we don't want to make another copy of because it
        # could be very large.
        mycount = defaultdict(list)
        r = Repeater(
            mycount, self.year, self.month, day=event.l_start_date.day,
            end_repeat=event.end_repeat, event=event, count_first=True,
            end_on=event.l_end_date.day, num=1
        )

        if event.starts_same_month_as(self.month):
            if not event.ends_same_month_as(self.month):
                # The chunk event starts this month,
                # but does NOT end this month
                r.end_on = None
        else:
            # event chunks can be maximum of 7 days, so if an event chunk
            # didn't start this month, we know it will end this month.
            r.day = 1
        r.repeat()
        # now we add in the events we generated to self.count
        for k, v in r.count.items():
            self.count[k].extend(v)

    def _handle_month_event(self, event):
        if event.is_chunk():
            self._handle_single_chunk(event)
        elif event.repeats('WEEKDAY'):
            if event.l_start_date.weekday() not in (5, 6):
                self.count[event.l_start_date.day].append(
                    (event.title, event.pk)
                )
        else:
            self.count[event.l_start_date.day].append((event.title, event.pk))

    def get_count(self):
        kwargs = {'year': self.year, 'month': self.month, 'count': self.count}
        for event in self.events:
            kwargs['event'] = event
            if event.starts_ends_yr_mo(self.year, self.month):
                self._handle_month_event(event)
            if event.repeats('WEEKLY') or event.repeats('BIWEEKLY'):
                r = WeeklyRepeater(**kwargs)
            elif event.repeats('MONTHLY'):
                r = MonthlyRepeater(**kwargs)
            elif event.repeats('DAILY') or event.repeats('WEEKDAY'):
                r = DailyRepeater(**kwargs)
            else:
                r = YearlyRepeater(**kwargs)
            self.count = r.repeat_it()
        return self.count
