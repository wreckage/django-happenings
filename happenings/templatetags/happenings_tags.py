from __future__ import unicode_literals

from itertools import chain

from django.template import Library
from django.conf import settings
from django.utils import timezone

from happenings.utils import repeater
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
    month_events = Event.objects.month_events(year, month, category, tag)
    repeat_events = Event.objects.repeat(year, month, category, tag)
    all_month_events = list(set(chain(repeat_events, month_events)))
    all_month_events.sort(key=lambda x: x.start_date)
    qs = req.META['QUERY_STRING']
    if qs:  # get any querystrings that are not next/prev
        qs = get_qs(qs)
    return month_display(
        year, month, all_month_events,
        month_events, repeat_events, start_day, net, qs, mini=mini
    )


@register.inclusion_tag('happenings/partials/upcoming_events.html')
def upcoming_events(now=timezone.localtime(timezone.now()), finish=90, num=5):
    finish = now + timezone.timedelta(days=finish)
    all_upcoming = (repeater.upcoming_events(x, now, finish, num)
                    for x in Event.objects.live(now))
    upcoming = sorted(
        (item for sublist in all_upcoming for item in sublist)
    )[:num]
    return {'upcoming_events': upcoming}
