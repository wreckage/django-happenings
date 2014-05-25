# Used to generate upcoming events

from __future__ import unicode_literals

from datetime import timedelta, date, datetime

from django.utils.timezone import make_aware, get_default_timezone
from django.utils.six.moves import xrange

from happenings.utils.common import inc_month


def _yearly(event, now, finish, num=5):
    events = []
    year = now.year
    if event.l_start_date > now:  # event starts in the future
        year = event.l_start_date.year
    elif now.month > event.l_start_date.month:  # event occurred this year yet?
        year += 1
    # equal to? The event occurs this month, so check the day to see if passed
    elif now.month == event.l_start_date.month:
        if now.day > event.l_start_date.day:  # greater than? already occurred
            year += 1
    month = event.l_start_date.month
    day = event.l_start_date.day
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
        if start > finish or \
                event.end_repeat is not None and start_ > event.end_repeat:
            return events
        events.append((start, event))
        year += 1
        num -= 1
    return events


def _monthly(event, now, finish, num=5):
    events = []
    year = now.year
    month = now.month
    if event.l_start_date > now:  # event starts in the future
        year = event.l_start_date.year
        month = event.l_start_date.month
    elif now.day > event.l_start_date.day:  # passed the event this month?
        month, year = inc_month(month, year)
    day = event.l_start_date.day
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
            month, year = inc_month(month, year)
            continue
        if start > finish or \
                event.end_repeat is not None and start_ > event.end_repeat:
            return events
        events.append((start, event))
        month, year = inc_month(month, year)
        num -= 1
    return events


def _weekday(event, now, finish, num=5):
    events = []
    if event.l_start_date > now:
        start = event.l_start_date
    else:
        start = now
    while start.weekday() > 4:
        start += timedelta(days=1)
    for i in xrange(num):
        # change to date() so we can compare to event.end_repeat
        start_ = date(start.year, start.month, start.day)
        if start > finish or \
                event.end_repeat is not None and start_ > event.end_repeat:
            return events
        while start.weekday() > 4:
            start += timedelta(days=1)
        events.append((start, event))
        start += timedelta(days=1)
    return events


def _others(event, now, finish, num=5):
    events = []
    repeat = {'WEEKLY': 7, 'BIWEEKLY': 14, 'DAILY': 1}
    if event.repeats('DAILY'):
        if event.l_start_date > now:
            start = event.l_start_date
        else:
            start = now
    else:
        start = event.l_start_date
        end = event.l_end_date
        while end <= now:
            start += timedelta(days=repeat[event.repeat])
            end += timedelta(days=repeat[event.repeat])
    for i in xrange(num):
        # change to date() so we can compare to event.end_repeat
        start_ = date(start.year, start.month, start.day)
        if start > finish or \
                event.end_repeat is not None and start_ > event.end_repeat:
            return events
        events.append((start, event))
        start += timedelta(days=repeat[event.repeat])
    return events


def upcoming_events(event, now, finish, num=5):
    """
    Repeats an event and returns 'num' (or fewer) upcoming events from 'now'.
    """
    events = []
    if event.repeats('NEVER'):
        if event.end_date < now:
            return events
        events.append((event.l_start_date, event))
        return events
    if event.repeats('WEEKDAY'):
        events = _weekday(event, now, finish, num)
    elif event.repeats('MONTHLY'):
        events = _monthly(event, now, finish, num)
    elif event.repeats('YEARLY'):
        events = _yearly(event, now, finish, num)
    else:
        events = _others(event, now, finish, num)
    return events
