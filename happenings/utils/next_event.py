from __future__ import unicode_literals

from datetime import date

from .common import check_weekday, inc_month
from .handlers import CountHandler


def get_next_event(event, now):
    """
    Returns the next occurrence of a given event, relative to 'now'.
    The 'event' arg should be an iterable containing one element,
    namely the event we'd like to find the occurrence of.
    The reason for this is b/c the get_count() function of CountHandler,
    which this func makes use of, expects an iterable.
    CHANGED: The 'now' arg must be an instance of datetime.datetime()
    to allow time comparison (used to accept datetime.date() as well)
    """
    year = now.year
    month = now.month
    day = now.day
    e_day = event[0].l_start_date.day
    e_end_day = event[0].l_end_date.day
    good_today = True if event[0].l_start_date.time() >= now.time() else False
    if event[0].starts_same_year_month_as(year, month) and \
            e_day <= now.day <= e_end_day:
        occurrences = CountHandler(year, month, event).get_count()
        future_dates = (x for x in occurrences if x >= now.day)
        day = min(future_dates, key=lambda x: abs(x - now.day))
    else:
        e_year = event[0].l_start_date.year
        e_month = event[0].l_start_date.month
        # convert to datetime.date() to be sure we can make a comparison
        if date(e_year, e_month, e_day) > date(now.year, now.month, now.day):
            # if the event hasn't started yet, then its next occurrence will
            # be on its start date, so return that.
            year = e_year
            month = e_month
            day = e_day
        else:
            occurrences = CountHandler(year, month, event).get_count()
            future_dates = [x for x in occurrences if x >= now.day]
            e_end_month = event[0].l_end_date.month
            if future_dates and future_dates[0] is day and not good_today:
                future_dates.pop(0)
            while not future_dates:
                month, year = inc_month(month, year)
                if event[0].repeats('YEARLY') and \
                        (month != e_month or month != e_end_month):
                    continue
                occurrences = CountHandler(year, month, event).get_count()
                # we don't check for now.day here, b/c we're in a month past
                # whatever now is. As an example, if we checked for now.day
                # we'd get stuck in an infinite loop if this were a
                # monthly repeating event and our 'now' was on a day after the
                # event's l_end_date.day
                future_dates = [x for x in occurrences]
            day = min(future_dates)

    if event[0].repeats('WEEKDAY'):
        return check_weekday(year, month, day)

    return year, month, day
