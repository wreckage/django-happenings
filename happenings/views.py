from __future__ import unicode_literals

from datetime import date
from calendar import month_name
from itertools import chain

from django.views.generic import ListView, DetailView
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Event
from happenings.utils.displays import month_display, day_display
from happenings.utils.next_event import get_next_event
from happenings.utils.mixins import JSONResponseMixin
from happenings.utils import common as c


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

        if not 'cal_ignore=true' in qs:
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

        context['month_and_year'] = "%(month)s, %(year)d" % (
            {'month': month_name[month], 'year': year}
        )

        if error:  # send any year/month errors
            context['cal_error'] = error

        month_events = Event.objects.month_events(
            year, month, self.category, self.tag
        )
        repeat_events = Event.objects.repeat(
            year, month, self.category, self.tag
        )

        # Using set ensures we don't have duplicates. List enables sorting.
        all_month_events = list(set(chain(repeat_events, month_events)))
        all_month_events.sort(key=lambda x: x.start_date)

        start_day = getattr(settings, "CALENDAR_START_DAY", 0)
        context['calendar'] = month_display(
            year, month, all_month_events,
            month_events, repeat_events, start_day, self.net, qs, mini
        )

        context['show_events'] = False
        if getattr(settings, "CALENDAR_SHOW_LIST", False):
            context['show_events'] = True
            context['events'] = c.order_events(all_month_events, d=True) \
                if self.request.is_ajax() else c.order_events(all_month_events)

        return context


class EventDayView(GenericEventView):
    template_name = 'happenings/event_day_list.html'

    def get_context_data(self, **kwargs):
        context = super(EventDayView, self).get_context_data(**kwargs)

        kw = self.kwargs
        y, m, d = map(int, (kw['year'], kw['month'], kw['day']))
        year, month, day, error = c.clean_year_month_day(y, m, d, self.net)

        if error:
            context['cal_error'] = error

        month_events = Event.objects.month_events(
            year, month, self.category, self.tag
        )
        repeat_events = Event.objects.repeat(
            year, month, self.category, self.tag
        )

        context['events'] = day_display(
            year, month, month_events, repeat_events, day
        )

        context['month'] = month_name[month]
        context['month_num'] = month
        context['year'] = year
        context['day'] = day
        context['month_day_year'] = "%(month)s %(day)d, %(year)d" % (
            {'month': month_name[month], 'day': day, 'year': year}
        )

        # for use in the template to build next & prev querystrings
        context['next'], context['prev'] = c.get_next_and_prev(self.net)
        return context


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'

    def get_object(self):
        return get_object_or_404(
            Event.objects.prefetch_related('location', 'categories', 'tags'),
            pk=self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        e = self.object

        for choice in Event.REPEAT_CHOICES:
            if choice[0] == e.repeat:
                context['repeat'] = choice[1]

        event = [e]  # event needs to be an iterable, see get_next_event()
        if not e.repeats('NEVER'):  # event is ongoing; get next occurrence
            if e.will_occur(c.now):
                year, month, day = get_next_event(event, c.now)
                context['next_event'] = dict(
                    year=year, month=month_name[month], day=day
                )
            else:  # event is finished repeating; get last occurrence
                end = e.end_repeat
                last_event = end
                if e.repeats('WEEKDAY'):
                    year, month, day = c.check_weekday(
                        end.year, end.month, end.day, reverse=True
                    )
                    last_event = date(year, month, day)
                context['last_event'] = last_event
        return context
