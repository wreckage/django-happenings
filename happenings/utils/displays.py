from __future__ import unicode_literals

import locale

from django.conf import settings

from happenings.models import Event
from .handlers import CountHandler
from .calendars import EventCalendar, MiniEventCalendar
from .common import get_next_and_prev

try:
    CALENDAR_LOCALE = str(getattr(settings, "CALENDAR_LOCALE", ""))
    locale.setlocale(locale.LC_ALL, CALENDAR_LOCALE)
except Exception:
    if CALENDAR_LOCALE == str(''):
        # locale.setlocale(x, '') failes with "Error: unsupported locale setting" on some systems
        CALENDAR_LOCALE = str('en_US.UTF-8')
        locale.setlocale(locale.LC_ALL, CALENDAR_LOCALE)
    else:
        # reraise: maybe wrong locale was set?
        raise


def add_occurrences(events, count):
    """
    Adds an occurrence key to the event object w/ a list of occurrences
    and adds a popover (for use with twitter bootstrap).
    The occurrence is added so that each event can be aware of what
    day(s) it occurs in the month.
    """
    for day in count:
        for item in count[day]:
            for event in events:
                if event.pk == item[1]:
                    try:
                        event.occurrence.append(day)
                    except AttributeError:
                        event.occurrence = []
                        event.occurrence.append(day)


def month_display(year, month, all_month_events,
                  start_day, net, qs, mini=False):
    """
    A function that returns an html calendar for the given
    month in the given year, with the number of events for that month
    shown on the generated calendar. Start_day is the day the calendar
    should start on (default is Monday).
    """
    # count the number of times events happen on a given day
    count = CountHandler(year, month, all_month_events).get_count()

    # sort count by start date using all_month_events (which is already sorted)
    for event in all_month_events[::-1]:
        for l in count.values():
            for item in l:
                if item[1] == event.pk:
                    l.insert(0, l.pop(l.index(item)))

    args = (year, month, count, all_month_events, start_day)
    if not mini:
        html_cal = EventCalendar(*args).formatmonth(year, month, net=net, qs=qs)
    else:
        html_cal = MiniEventCalendar(*args).formatmonth(year, month, net=net, qs=qs)

    nxt, prev = get_next_and_prev(net)
    extra_qs = ('&' + '&'.join(qs)) if qs else ''
    # inject next/prev querystring urls and make them aware of any querystrings
    # already present in the url
    html_cal = html_cal.replace(
        'class="month">\n<tr>',
        'class="month">\n<tr><th colspan="1" class="month-arrow-left">\
        <a href="?cal_prev=%d%s">&larr;</a></th>' % (prev, extra_qs)
    ).replace(
        '%d</th>' % year,
        '%d</th><th colspan="1" class="month-arrow-right">\
        <a href="?cal_next=%d%s">&rarr;</a></th>' % (year, nxt, extra_qs)
    )

    add_occurrences(all_month_events, count)

    return html_cal


def day_display(year, month, all_month_events, day):
    """
    Returns the events that occur on the given day.
    Works by getting all occurrences for the month, then drilling
    down to only those occurring on the given day.
    """
    # Get a dict with all of the events for the month
    count = CountHandler(year, month, all_month_events).get_count()
    pks = [x[1] for x in count[day]]  # list of pks for events on given day
    # List enables sorting.
    # See the comments in EventMonthView in views.py for more info
    day_events = list(Event.objects.filter(pk__in=pks).order_by(
        'start_date').prefetch_related('cancellations'))
    day_events.sort(key=lambda x: x.l_start_date.hour)
    return day_events
