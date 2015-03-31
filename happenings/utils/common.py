from __future__ import unicode_literals

from datetime import date, timedelta
from calendar import monthrange

from django.utils import timezone
from django.utils.six.moves import xrange


now = timezone.localtime(timezone.now())


def inc_month(month, year):
    """
    Increment the month and, if neccessary, the year.
    Both month and year should be ints.
    """
    month += 1
    if month > 12:
        month = 1
        year += 1
    return month, year


def _inc_day(year, month, day, net):
    """Increments the day by converting to a datetime.date()."""
    d = date(year, month, day)
    new_d = d + timezone.timedelta(days=net)
    return new_d.year, new_d.month, new_d.day


def get_net_category_tag(req):
    if req.META['QUERY_STRING']:
        net = get_net(req)
        category, tag = get_category_tag(req)
    else:
        net = 0
        category = None
        tag = None
    return net, category, tag


def get_net(req):
    """Get the net of any 'next' and 'prev' querystrings."""
    try:
        nxt, prev = map(
            int, (req.GET.get('cal_next', 0), req.GET.get('cal_prev', 0))
        )
        net = nxt - prev
    except Exception:
        net = 0
    return net


def get_category_tag(req):
    """Get value of any category and/or tag querystrings"""
    return req.GET.get('cal_category', None), req.GET.get('cal_tag', None)


def get_qs(old_qs):
    there = (
        'cal_mini', 'cal_next', 'cal_prev', 'cal_month', 'cal_year'
    )
    return [x for x in old_qs.split('&') if x.split('=')[0] not in there]


# TODO change from d to something more descriptive
def order_events(events, d=False):
    """
    Group events that occur on the same day, then sort them alphabetically
    by title, then sort by day. Returns a list of tuples that looks like
    [(day: [events])], where day is the day of the event(s), and [events]
    is an alphabetically sorted list of the events for the day.
    """
    ordered_events = {}
    for event in events:
        try:
            for occ in event.occurrence:
                try:
                    ordered_events[occ].append(event)
                except Exception:
                    ordered_events[occ] = [event]
        except AttributeError:  # no occurrence for this event
            # This shouldn't happen, since an event w/o an occurrence
            # shouldn't get this far, but if it does, just skip it since
            # it shouldn't be displayed on the calendar anyway.
            pass

    if d:
        # return as a dict without sorting by date
        return ordered_events
    else:
        # return ordered_events as a list tuples sorted by date
        return sorted(ordered_events.items())


def get_next_and_prev(net):
    """Returns what the next and prev querystrings should be."""
    if net == 0:
        nxt = prev = 1
    elif net > 0:
        nxt = net + 1
        prev = -(net - 1)
    else:
        nxt = net + 1
        prev = abs(net) + 1
    return nxt, prev


def _check_year(year, month, error, error_msg):
    """Checks that the year is within 50 years from now."""
    if year not in xrange((now.year - 50), (now.year + 51)):
        year = now.year
        month = now.month
        error = error_msg
    return year, month, error


def clean_year_month_day(year, month, day, net):
    error = False
    error_msg = "The date given was invalid."
    # check that the month is within 1-12
    if month not in xrange(1, 13):
        month = now.month
        error = error_msg
    # check that the day is within range for the month
    if day not in xrange(1, monthrange(year, month)[1] + 1):
        day = 1
        error = error_msg
    # if no error yet, increment the day by net then check the year
    if not error:
        year, month, day = _inc_day(year, month, day, net)
        year, month, error = _check_year(year, month, error, error_msg)
    return year, month, day, error


def clean_year_month(year, month, month_orig):
    """
    If 'month_orig', which is the month given in the url BEFORE any next/prev
    query strings have been applied, is out of range, sets month to the
    current month and returns an error message. Also Returns an error
    message if the year given is +/- 50 years from now.
    If 'month', which is the month given in the url AFTER any next/prev
    query strings have been applied, is out of range, adjusts it to be
    in range (by also adjusting the year).
    """
    error = False
    error_msg = "The date given was invalid."
    if month_orig not in xrange(1, 13) and month_orig is not None:
        month = now.month
        error = error_msg
    # This takes care of 'next' query strings making month > 12
    while month > 12:
        month -= 12
        year += 1
    # This takes care of 'prev' query strings making month < 1
    while month < 1:
        month += 12
        year -= 1
    year, month, error = _check_year(year, month, error, error_msg)
    return year, month, error


def check_weekday(year, month, day, reverse=False):
    """
    Make sure any event day we send back for weekday repeating
    events is not a weekend.
    """
    d = date(year, month, day)
    while d.weekday() in (5, 6):
        if reverse:
            d -= timedelta(days=1)
        else:
            d += timedelta(days=1)
    return d.year, d.month, d.day
