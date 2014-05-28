from __future__ import unicode_literals

from collections import defaultdict
from datetime import date, timedelta

from django.utils.six.moves import xrange


def _first_weekday(weekday, d):
    """
    Given a weekday and a date, will increment the date until it's
    weekday matches that of the given weekday, then that date is returned.
    """
    while weekday != d.weekday():
        d += timedelta(days=1)
    return d


# XXX Move this to another file. Maybe put into repeater.py, and
# change what was repeater.py to upcoming.py. Fix the tests!!
class Repeater(object):
    def __init__(self, count, year, month, day=None, end_repeat=None,
                 event=None, num=7, count_first=False, end_on=None):
        self.count = count
        self.year = year
        self.month = month
        self.day = day
        self.end_repeat = end_repeat
        self.event = event
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
        as we go along. Then return the count.
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
        return self.count

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
        return self.count

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
        return self.count

    def repeat_chunk(self, diff):
        for i in xrange(diff):
            self.count = self.repeat(self.day + i + 1)
        return self.count

    def repeat_biweekly(self):
        """
        This function is unique b/c it expects self.count to be an
        EMPTY defaultdict.
        """
        d = self.event.l_start_date
        while d.year != self.year or d.month != self.month:
            d += timedelta(days=14)
        self.day = d.day
        self.count = self.repeat()
        if self.event.is_chunk() and self.count:
            self.day = min(self.count)
            self.count = self.repeat_chunk(self.event.start_end_diff())
        return self.count


def _handle_yearly_repeat_chunk(year, month, count, event):
    r = Repeater(
        count, year, month, day=event.l_start_date.day,
        end_repeat=event.end_repeat, event=event, num=1
    )
    if event.l_start_date.month == month:
        if event.starts_ends_same_month():
            r.end_on = event.l_end_date.day
        count = r.repeat()
    elif (event.l_end_date.month == month
          and not event.starts_ends_same_month()):
        count = r.repeat_reverse(event.l_end_date.day, 1)
    return count


def _handle_yearly_repeat(year, month, count, event):
    """
    Events that repeat every year should be shown every year
    on the same date they started e.g. an event that starts on March 23rd
    would appear on March 23rd every year it is scheduled to repeat.
    If the event is a chunk event, hand it over to
    _handle_yearly_repeat_chunk().
    """
    # The start day will be counted if we're in the start year, so only count
    # the day if we're in the same month as l_start_date, but not in the
    # same year.
    if event.l_start_date.month == month and event.l_start_date.year != year:
        count[event.l_start_date.day].append((event.title, event.pk))
    # If we're in the same mo & yr as l_start_date, should already be filled in
    if event.is_chunk() and not event.starts_same_year_month_as(year, month):
        count = _handle_yearly_repeat_chunk(year, month, count, event)
    return count


def _handle_monthly_repeat_chunk(year, month, count, event):
    r = Repeater(
        count, year, month, end_repeat=event.end_repeat, event=event, num=1
    )
    start_day = event.l_start_date.day
    last_day_last_mo = date(year, month, 1) - timedelta(days=1)

    if not event.starts_same_year_month_as(year, month):
        if not event.starts_ends_same_month():
                r.day = start_day
                count = r.repeat()  # fill out the end of the month
                # fill out the beginning of the month, if nec.
                if start_day <= last_day_last_mo.day:
                    count = r.repeat_reverse(event.l_end_date.day, 1)
        else:
            count = r.repeat_reverse(event.l_end_date.day, start_day + 1)
    return count


def _handle_monthly_repeat(year, month, count, event):
    """
    Events that repeat every month should be shown every month
    on the same date they started e.g. an event that starts on the 23rd
    would appear on the 23rd every month it is scheduled to repeat.
    If the event is a chunk event, hand it over to
    _handle_monthly_repeat_chunk().
    """
    start_day = event.l_start_date.day
    if not event.starts_same_month_as(month):
        count[start_day].append((event.title, event.pk))
    elif event.starts_same_month_not_year_as(month, year):
        count[start_day].append((event.title, event.pk))

    if event.is_chunk():
        count = _handle_monthly_repeat_chunk(year, month, count, event)
    return count


def _handle_daily_repeat(year, month, count, event):
    """Handles repeating daily and every weekday."""
    r = Repeater(
        count, year, month, end_repeat=event.end_repeat, event=event
    )

    if event.starts_same_year_month_as(year, month):
        # we assume that l_start_date was already counted
        r.day = event.l_start_date.day
    else:
        # Note count_first=True b/c although the start date isn't this month,
        # the event does begin repeating this month and start_date has
        # not yet been counted.
        r.day = date(year, month, 1).day
        r.count_first = True

    if event.repeats('DAILY'):
        r.num = 1
        count = r.repeat()
    else:
        count = r.repeat_weekdays()

    return count


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


def _handle_weekly_repeat_out(year, month, count, event):
    """
    Handles repeating an event weekly (or biweekly) if the current
    year and month are outside of it's start year and month.
    It takes care of cases 3 and 4 in _handle_weekly_repeat_in() comments.
    """
    start_d = _first_weekday(
        event.l_start_date.weekday(), date(year, month, 1)
    )
    r = Repeater(
        count, year, month, day=start_d.day, end_repeat=event.end_repeat,
        event=event, count_first=True, num=7
    )

    if event.repeats('BIWEEKLY'):
        r.count = defaultdict(list)  # repeat_biweekly works w/ an empty dict
        r.num = 14
        mycount = r.repeat_biweekly()
        if mycount:
            if event.is_chunk() and min(mycount) not in xrange(1, 8):
                diff = event.start_end_diff()
                mycount = _chunk_fill_out_first_week(
                    year, month, mycount, event, diff
                )
            count.update(mycount)  # update count w/ biweekly events

    elif event.repeats('WEEKLY'):
        # Note count_first=True b/c although the start date isn't this month,
        # the event does begin repeating this month and start_date has
        # not yet been counted.
        # Also note we start from start_d.day and not event.l_start_date.day
        r = Repeater(
            count, year, month, day=start_d.day, end_repeat=event.end_repeat,
            event=event, count_first=True, num=7
        )
        count = r.repeat()
        if event.is_chunk():
            diff = event.start_end_diff()
            count = _chunk_fill_out_first_week(year, month, count, event, diff)
            for i in xrange(diff):
                # count the chunk days, then repeat them
                r.day = start_d.day + i + 1
                count = r.repeat()
    return count


def _handle_weekly_repeat_in(year, month, count, event):
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
    repeats = {'WEEKLY': 7, 'BIWEEKLY': 14}
    r = Repeater(
        count, year, month, day=event.l_start_date.day,
        end_repeat=event.end_repeat, event=event, count_first=True
    )
    if event.starts_same_year_month_as(year, month):
        # This takes care of 1 and 2 above.
        # Note that 'count' isn't incremented before adding a week (in
        # Repeater.repeat()), b/c it's assumed that l_start_date was already
        # counted.
        for repeat, num in repeats.items():
            r.num = num
            if event.repeats(repeat):
                count = r.repeat()
                if event.is_chunk():
                    r.repeat_chunk(diff=event.start_end_diff())
    return count


def _handle_single_chunk(year, month, count, event):
    """
    This handles either a non-repeating event chunk, or the first
    month of a repeating event chunk.
    """
    if not event.starts_same_month_as(month) and not event.repeats('NEVER'):
        # we don't want repeating chunk events if we're not in it's start month
        return count

    r = Repeater(
        count, year, month, day=event.l_start_date.day,
        end_repeat=event.end_repeat, event=event, count_first=True,
        end_on=event.l_end_date.day, num=1
    )

    if event.starts_same_month_as(month):
        if not event.ends_same_month_as(month):
            # The chunk event starts this month, but does NOT end this month
            r.end_on = None
    else:
        # event chunks can be maximum of 7 days, so if an event chunk
        # didn't start this month, we know it will end this month.
        r.day = 1
    count = r.repeat()
    return count


def _handle_month_events(year, month, count, month_events):
    for event in month_events:
        if event.is_chunk():
            count = _handle_single_chunk(year, month, count, event)
        elif event.repeats('WEEKDAY'):
            if event.l_start_date.weekday() not in (5, 6):
                count[event.l_start_date.day].append((event.title, event.pk))
        else:
            count[event.l_start_date.day].append((event.title, event.pk))
    return count


def _handle_repeat_events(year, month, count, repeat_events):
    for event in repeat_events:
        args = (year, month, count, event)
        if event.repeats('WEEKLY') or event.repeats('BIWEEKLY'):
            if event.starts_same_year_month_as(year, month):
                count = _handle_weekly_repeat_in(*args)
            else:
                count = _handle_weekly_repeat_out(*args)
        elif event.repeats('MONTHLY'):
            count = _handle_monthly_repeat(*args)
        elif event.repeats('DAILY') or event.repeats('WEEKDAY'):
            count = _handle_daily_repeat(*args)
        else:
            count = _handle_yearly_repeat(*args)
    return count


def handle_count(year, month, month_events, repeat_events):
    """
    Used by month_display() to handle sending the counter off
    to the appropriate handler function for counting the event days
    for the given month in the given year. Returns the counter.
    """
    count = defaultdict(list)
    # month events contains all events that start or end within
    # this month, this year
    count = _handle_month_events(year, month, count, month_events)
    count = _handle_repeat_events(year, month, count, repeat_events)
    return count
