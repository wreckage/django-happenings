from __future__ import unicode_literals

import locale

from django.conf import settings

from happenings.models import Event
from .handlers import handle_count
from .calendars import EventCalendar, MiniEventCalendar
from .common import get_next_and_prev

LOC = str(getattr(settings, "CALENDAR_LOCALE", "en_US.utf8"))
locale.setlocale(locale.LC_ALL, LOC)


def _add_occurrence_and_popover(events, cal, mini, count):
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
                    if mini:  # add popover content if mini calendar
                        t = "%I:%M%p" if event.l_start_date.minute else "%I%p"
                        title = event.l_start_date.strftime(t).lstrip('0') + \
                            ' - ' + event.title
                        cal = cal.replace(
                            '>%d</a><div data-content="<ul>' % day,
                            ('>%d</a><div data-content="<ul>'
                             '<li><a href=\'%s\'>%s</a></li>' % (
                                 day, event.get_absolute_url(), title)
                             )
                        )
    return cal


def month_display(year, month, all_month_events,
                  month_events, repeat_events, start_day, net, qs, mini=False):
    """
    A function that returns an html calendar for the given
    month in the given year, with the number of events for that month
    shown on the generated calendar. Start_day is the day the calendar
    should start on (default is Monday).
    """
    # count the number of times events happen on a given day
    count = handle_count(year, month, month_events, repeat_events)

    # sort count by start date using all_month_events (which is already sorted)
    for event in all_month_events[::-1]:
        for l in count.values():
            for item in l:
                if item[1] == event.pk:
                    l.insert(0, l.pop(l.index(item)))

    if not mini:
        html_cal = EventCalendar(
            year, month, count, all_month_events, start_day, LOC
        ).formatmonth(year, month)
    else:
        html_cal = MiniEventCalendar(
            year, month, count, start_day, LOC
        ).formatmonth(year, month)

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

    html_cal = _add_occurrence_and_popover(
        all_month_events, html_cal, mini, count
    )

    return html_cal


def day_display(year, month, month_events, repeat_events, day):
    """Returns the events that occur on the given day."""
    # Get a dict with all of the events for the month
    count = handle_count(year, month, month_events, repeat_events)
    # Create a set consisting of the pks of only those events that
    # occur on the given day
    pks = [x[1] for x in count[day]]
    return Event.objects.filter(pk__in=pks).order_by('start_date')
