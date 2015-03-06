# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python lib:
from datetime import date, timedelta
from calendar import month_name

# django:
from django.views.generic import ListView, DetailView
from django.conf import settings
from django.shortcuts import get_object_or_404

# thirdparties:
import six

# happenings:
from .models import Event
from happenings.utils.displays import month_display, day_display
from happenings.utils.next_event import get_next_event
from happenings.utils.mixins import JSONResponseMixin
from happenings.utils import common as c


CALENDAR_LOCALE = getattr(settings, 'CALENDAR_LOCALE', 'en_US.utf8')


class GenericEventView(JSONResponseMixin, ListView):
    model = Event

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            return self.render_to_json_response(context, **kwargs)
        return super(GenericEventView, self).render_to_response(
            context, **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(GenericEventView, self).get_context_data(**kwargs)

        self.net, self.category, self.tag = c.get_net_category_tag(
            self.request
        )

        if self.category is not None:
            context['cal_category'] = self.category
        if self.tag is not None:
            context['cal_tag'] = self.tag
        return context


class EventMonthView(GenericEventView):
    template_name = 'happenings/event_month_list.html'

    def get_year_and_month(self, net, qs, **kwargs):
        """
        Get the year and month. First tries from kwargs, then from
        querystrings. If none, or if cal_ignore qs is specified,
        sets year and month to this year and this month.
        """
        year = c.now.year
        month = c.now.month + net
        month_orig = None

        if 'cal_ignore=true' not in qs:
            if 'year' and 'month' in self.kwargs:  # try kwargs
                year, month_orig = map(
                    int, (self.kwargs['year'], self.kwargs['month'])
                )
                month = month_orig + net
            else:
                try:  # try querystring
                    year = int(self.request.GET['cal_year'])
                    month_orig = int(self.request.GET['cal_month'])
                    month = month_orig + net
                except Exception:
                    pass
        # return the year and month, and any errors that may have occurred do
        # to an invalid month/year being given.
        return c.clean_year_month(year, month, month_orig)

    def get_month_events(self, *args, **kwargs):
        return Event.objects.all_month_events(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventMonthView, self).get_context_data(**kwargs)

        qs = self.request.META['QUERY_STRING']

        year, month, error = self.get_year_and_month(self.net, qs)

        mini = True if 'cal_mini=true' in qs else False

        # get any querystrings that are not next/prev/year/month
        if qs:
            qs = c.get_qs(qs)

        # add a dict containing the year, month, and month name to the context
        current = dict(
            year=year, month_num=month, month=month_name[month][:3]
        )
        context['current'] = current

        display_month = month_name[month]

        if isinstance(display_month, six.binary_type):
            display_month = display_month.decode('utf-8')

        context['month_and_year'] = u"%(month)s, %(year)d" % (
            {'month': display_month, 'year': year}
        )

        if error:  # send any year/month errors
            context['cal_error'] = error

        # List enables sorting. As far as I can tell, .order_by() can't be used
        # here because we need it ordered by l_start_date.hour (simply ordering
        # by start_date won't work). The only alternative I've found is to use
        # extra(), but this would likely require different statements for
        # different databases...
        all_month_events = list(self.get_month_events(
            year, month, self.category, self.tag, loc=True, cncl=True
        ))

        all_month_events.sort(key=lambda x: x.l_start_date.hour)

        start_day = getattr(settings, "CALENDAR_START_DAY", 0)
        context['calendar'] = month_display(
            year, month, all_month_events, start_day, self.net, qs, mini
        )

        context['show_events'] = False
        if getattr(settings, "CALENDAR_SHOW_LIST", False):
            context['show_events'] = True
            context['events'] = c.order_events(all_month_events, d=True) \
                if self.request.is_ajax() else c.order_events(all_month_events)

        return context


class EventDayView(GenericEventView):
    template_name = 'happenings/event_day_list.html'

    def check_for_cancelled_events(self, d):
        """Check if any events are cancelled on the given date 'd'."""
        for event in self.events:
            for cn in event.cancellations.all():
                if cn.date == d:
                    event.title += ' (CANCELLED)'

    def get_month_events(self, *args, **kwargs):
        return Event.objects.all_month_events(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventDayView, self).get_context_data(**kwargs)

        kw = self.kwargs
        y, m, d = map(int, (kw['year'], kw['month'], kw['day']))
        year, month, day, error = c.clean_year_month_day(y, m, d, self.net)

        if error:
            context['cal_error'] = error

        # Note that we don't prefetch 'cancellations' because they will be
        # prefetched later (in day_display in displays.py)
        all_month_events = self.get_month_events(
            year, month, self.category, self.tag
        )

        self.events = day_display(
            year, month, all_month_events, day
        )

        self.check_for_cancelled_events(d=date(year, month, day))
        context['events'] = self.events

        display_month = month_name[month]
        if isinstance(display_month, six.binary_type):
            display_month = display_month.decode('utf-8')

        context['month'] = display_month
        context['month_num'] = month
        context['year'] = year
        context['day'] = day
        context['month_day_year'] = u"%(month)s %(day)d, %(year)d" % (
            {'month': display_month, 'day': day, 'year': year}
        )

        # for use in the template to build next & prev querystrings
        context['next'], context['prev'] = c.get_next_and_prev(self.net)
        return context


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_object(self):
        return get_object_or_404(
            Event.objects.prefetch_related(
                'location', 'categories', 'tags', 'cancellations'
            ),
            pk=self.kwargs['pk']
        )

    def get_cncl_days(self):
        cncl = self.object.cancellations.all()
        return [(x.date, x.reason) for x in cncl if x.date >= c.now.date()]

    def check_cncl(self, d):
        cncl = self.object.cancellations.all()
        return True if [x for x in cncl if x.date == d] else False

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        e = self.object

        for choice in Event.REPEAT_CHOICES:
            if choice[0] == e.repeat:
                context['repeat'] = choice[1]

        context['cncl_days'] = self.get_cncl_days()

        event = [e]  # event needs to be an iterable, see get_next_event()
        if not e.repeats('NEVER'):  # event is ongoing; get next occurrence
            if e.will_occur(c.now):
                year, month, day = get_next_event(event, c.now)
                next_event = date(year, month, day)
                context['next_event'] = date(year, month, day)
                context['next_or_prev_cncl'] = self.check_cncl(next_event)
            else:  # event is finished repeating; get last occurrence
                end = e.end_repeat
                last_event = end
                if e.repeats('WEEKDAY'):
                    year, month, day = c.check_weekday(
                        end.year, end.month, end.day, reverse=True
                    )
                    last_event = date(year, month, day)
                context['last_event'] = last_event
                context['next_or_prev_cncl'] = self.check_cncl(last_event)
        else:
            if e.is_chunk():
                # list of days for single-day event chunk
                context['event_days'] = (  # list comp
                    (e.l_start_date + timedelta(days=x))
                    for x in range(e.start_end_diff() + 1)
                )
            else:
                # let template know if this single-day, non-repeating event is
                # cancelled
                context['this_cncl'] = self.check_cncl(e.l_start_date.date())
        return context
