from __future__ import unicode_literals

import heapq
import datetime

from django.template import Library
from django.conf import settings
from django.utils import timezone

from happenings.utils.upcoming import UpcomingEvents
from happenings.models import Event
from happenings.utils.displays import month_display
from happenings.utils.common import (
    get_net_category_tag,
    get_qs,
    clean_year_month,
    now
)

register = Library()
start_day = getattr(settings, "CALENDAR_START_DAY", 0)


@register.simple_tag
def show_calendar(req, mini=False):
    net, category, tag = get_net_category_tag(req)
    year = now.year
    month = now.month + net
    year, month, error = clean_year_month(year, month, None)

    prefetch = {'loc': True, 'cncl': True}
    if mini:
        prefetch['loc'] = False  # locations aren't displayed on mini calendar

    all_month_events = list(Event.objects.all_month_events(
        year, month, category, tag, **prefetch
    ))
    all_month_events.sort(key=lambda x: x.l_start_date.hour)
    qs = req.META['QUERY_STRING']
    if qs:  # get any querystrings that are not next/prev
        qs = get_qs(qs)
    return month_display(
        year, month, all_month_events, start_day, net, qs, mini=mini
    )


@register.inclusion_tag('happenings/partials/upcoming_events.html')
def upcoming_events(now=timezone.localtime(timezone.now()), finish=90, num=5):
    finish = now + timezone.timedelta(days=finish)
    all_upcoming = (UpcomingEvents(x, now, finish, num).get_upcoming_events()
                    for x in Event.objects.live(now))
    upcoming = heapq.nsmallest(
        num,
        (item for sublist in all_upcoming for item in sublist),
        key=lambda x: x[0]
    )
    return {'upcoming_events': upcoming}


@register.filter
def to_datetime(day, date):
    """
    Filter - Creates a new datetime using the month and year from 'date'
    and the day from 'day'
    """
    return datetime.datetime(date.year, date.month, day)


@register.filter
def return_item(l, i):
    """
    Filter - Returns item at position i in l.
    See: http://stackoverflow.com/a/13376792
    """
    try:
        return l[i]
    except Exception:
        return None


@register.filter
def stl(l):
    """Filter - Returns 2nd to last item in list l"""
    return l[-2]
