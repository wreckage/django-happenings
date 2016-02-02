# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python lib:
from calendar import LocaleHTMLCalendar, HTMLCalendar, month_name
from datetime import date
import sys

# django:
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.dates import WEEKDAYS, WEEKDAYS_ABBR
from django.utils.html import mark_safe

# thirdparties:
import six

# happenings:
from .common import get_now, get_next_and_prev

URL = getattr(settings, "CALENDAR_URL", 'calendar')
URLS_NAMESPACE = getattr(settings, "CALENDAR_URLS_NAMESPACE", 'calendar')

CALENDAR_LOCALE = getattr(settings, 'CALENDAR_LOCALE', 'en_US.utf8')

LEGACY_CALENDAR_HOUR_FORMAT = LEGACY_CALENDAR_TIME_FORMAT = getattr(settings, 'CALENDAR_LEGACY_TIME_FORMAT', "%I:%M%p")


if '%p' in LEGACY_CALENDAR_TIME_FORMAT:
    LEGACY_CALENDAR_HOUR_FORMAT = LEGACY_CALENDAR_TIME_FORMAT.replace('%M', '')


CALENDAR_TIME_FORMAT = getattr(settings, 'CALENDAR_TIME_FORMAT', "TIME_FORMAT")

CALENDAR_HOUR_FORMAT = getattr(settings, 'CALENDAR_HOUR_FORMAT', '')

if not CALENDAR_HOUR_FORMAT:
    CALENDAR_HOUR_FORMAT = CALENDAR_TIME_FORMAT
    if not CALENDAR_HOUR_FORMAT.endswith('_FORMAT'):
        for char in ('i', 's', 'u'):
            CALENDAR_HOUR_FORMAT = CALENDAR_HOUR_FORMAT.replace(':'+char, '')
            CALENDAR_HOUR_FORMAT = CALENDAR_HOUR_FORMAT.replace('.'+char, '')
            CALENDAR_HOUR_FORMAT = CALENDAR_HOUR_FORMAT.replace(char, '')
        CALENDAR_HOUR_FORMAT = CALENDAR_HOUR_FORMAT.strip(':')


class GenericCalendar(HTMLCalendar):
    def __init__(self, year, month, count, all_month_events, firstweekday=0, request=None, base_context=None, *args, **kwargs):
        super(GenericCalendar, self).__init__(firstweekday)
        self.yr = year
        self.mo = month
        self.count = count  # defaultdict in {date:[(title1, pk1), (title2, pk2),]} format
        self.events = all_month_events
        self.request = request
        self.base_context = base_context or {}
        self._context = None

#    def add_occurrence(self):
#        try:
#            self.event.occurrence.append(self.day)
#        except AttributeError:
#            self.event.occurrence = []
#            self.event.occurrence.append(self.day)

    def get_context(self, day=None):
        if self._context is None:
            now = get_now()
            context = dict(self.base_context)
            context.update({
                'URLS_NAMESPACE': URLS_NAMESPACE,
                'CALENDAR_TIME_FORMAT': CALENDAR_TIME_FORMAT,
                'CALENDAR_HOUR_FORMAT': CALENDAR_HOUR_FORMAT,
                'calendar': self,
                'is_current_day': False,
                'now': now,
                'request': self.request,
            })
            self._context = context
        return dict(self._context)

    def check_if_cancelled(self):
        d = date(self.yr, self.mo, self.day)
        is_cancelled = self.event.check_if_cancelled(d)
        if is_cancelled:
            self.title += " (CANCELLED)"
        return is_cancelled

    def get_day_url(self, day):
        if URLS_NAMESPACE:
            url_name = '%s:day_list' % (URLS_NAMESPACE)
        else:
            url_name = 'day_list'
        return reverse(url_name, args=(self.yr, self.mo, day))

    def formatmonth(self, theyear, themonth, withyear=True, net=None, qs=None, template='happenings/partials/calendar/month_table.html'):
        """Return a formatted month as a table."""
        context = self.get_context()
        context['month_start_date'] = date(self.yr, self.mo, 1)
        context['week_rows'] = []
        for week in self.monthdays2calendar(theyear, themonth):
            week_row = []
            for day, weekday in week:
                week_row.append(self.formatday(day, weekday))
            context['week_rows'].append(week_row)

        nxt, prev = get_next_and_prev(net)
        extra_qs = ('&' + '&'.join(qs)) if qs else ''
        context['prev_qs'] = mark_safe('?cal_prev=%d%s' % (prev, extra_qs))
        context['next_qs'] = mark_safe('?cal_next=%d%s' % (nxt, extra_qs))
        context['withyear'] = withyear
        return render_to_string(template, context)


class EventCalendar(GenericCalendar):

    def popover_helper(self):
        self.when = ''
        self.where = ''
        self.desc = ''
        self.title2 = ''

    def formatday(
            self, day, weekday,
            day_template='happenings/partials/calendar/day_cell.html',
            noday_template='happenings/partials/calendar/day_noday_cell.html',
            popover_template='happenings/partials/calendar/popover.html',
            ):
        """Return a day as a table cell."""
        super(EventCalendar, self).formatday(day, weekday)
        now = get_now()
        context = self.get_context()
        context['events'] = []
        context['day'] = day
        context['day_url'] = self.get_day_url(day)
        context['month_start_date'] = date(self.yr, self.mo, 1)
        context['weekday'] = weekday
        context['cssclass'] = self.cssclasses[weekday]
        context['popover_template'] = popover_template
        context['num_events'] = len(self.count.get(day, [])),
        try:
            processed_date = date(self.yr, self.mo, day)
        except ValueError:
            # day is out of range for month
            processed_date = None

        context['month_start_date'] = date(self.yr, self.mo, 1)

        if day == 0:
            template = noday_template
        else:
            template = day_template

        if now.date() == processed_date:
            context['is_current_day'] = True

        if processed_date and (day in self.count):
            for item in self.count[day]:
                self.pk = item[1]
                self.title = item[0]
                for event in self.events:
                    if event.pk == self.pk:
                        event.check_if_cancelled(processed_date)
                        # allow to use event.last_check_if_cancelled and populate event.title.extra

                        context['events'].append(event)

        return render_to_string(template, context)


class MiniEventCalendar(EventCalendar):
    def __init__(self, *args, **kwargs):
        super(MiniEventCalendar, self).__init__(*args, **kwargs)
        # Change count from a defaultdict to a regular dict, so that when we
        # try and check if there are days in count, they won't be added if they
        # aren't there.
        self.count = dict(self.count)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        return super(MiniEventCalendar, self).formatday(
            day, weekday,
            day_template='happenings/partials/calendar/mini_day_cell.html',
            popover_template='happenings/partials/calendar/mini_popover.html',
        )


class LegacyGenericCalendar(LocaleHTMLCalendar):
    def __init__(self, year, month, count, all_month_events, *args):
        if len(args) < 2:
            args = args + (CALENDAR_LOCALE, )
        super(GenericCalendar, self).__init__(*args)
        if isinstance(self.locale, tuple):
            if len(self.locale) == 2:
                self.encoding = self.locale[1]
        elif self.locale.find('.') > 0:
            self.encoding = self.locale.split('.')[1]
        else:
            self.encoding = None
        self.yr = year
        self.mo = month
        self.count = count  # defaultdict in {date:[(title1, pk1), (title2, pk2),]} format
        self.events = all_month_events

#    def add_occurrence(self):
#        try:
#            self.event.occurrence.append(self.day)
#        except AttributeError:
#            self.event.occurrence = []
#            self.event.occurrence.append(self.day)

    def check_if_cancelled(self):
        d = date(self.yr, self.mo, self.day)
        is_cancelled = self.event.check_if_cancelled(d)
        if is_cancelled:
            self.title += " (CANCELLED)"
        return is_cancelled

    def formatday(self, day, weekday):
        """Set some commonly used variables."""
        self.wkday_not_today = '<td class="%s"><div class="td-inner">' % (
            self.cssclasses[weekday])

        self.wkday_today = (
            '<td class="%s calendar-today"><div class="td-inner">' % (
                self.cssclasses[weekday])
        )
        if URLS_NAMESPACE:
            url_name = '%s:day_list' % (URLS_NAMESPACE)
        else:
            url_name = 'day_list'

        self.day_url = reverse(url_name, args=(self.yr, self.mo, day))
        self.day = day

        self.anch = '<a href="%s">%d</a>' % (
            self.day_url, day
        )

        self.end = '</div></td>'

    def get_display_month(self, themonth):
        display_month = month_name[themonth]

        if isinstance(display_month, six.binary_type) and self.encoding:
            display_month = display_month.decode(self.encoding)
        return display_month

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Change colspan to "5", add "today" button, and return a month
        name as a table row.
        """
        display_month = month_name[themonth]

        if isinstance(display_month, six.binary_type) and self.encoding:
            display_month = display_month.decode(self.encoding)

        if withyear:
            s = u'%s %s' % (display_month, theyear)
        else:
            s = u'%s' % display_month
        return ('<tr><th colspan="5" class="month">'
                '<button id="cal-today-btn" class="btn btn-small">'
                'Today</button> %s</th></tr>' % s)



class LegacyEventCalendar(LegacyGenericCalendar):
    def popover_helper(self):
        """Populate variables used to build popovers."""
        # when
        display_month = month_name[self.mo]

        if isinstance(display_month, six.binary_type) and self.encoding:
            display_month = display_month.decode('utf-8')

        self.when = ('<p><b>When:</b> ' + display_month + ' ' +
                     str(self.day) + ', ' + self.event.l_start_date.strftime(
                         LEGACY_CALENDAR_TIME_FORMAT).lstrip('0') + ' - ' +
                     self.event.l_end_date.strftime(LEGACY_CALENDAR_TIME_FORMAT).lstrip('0') +
                     '</p>')

        if self.event.location.exists():  # where
            self.where = '<p><b>Where:</b> '
            for l in self.event.location.all():
                self.where += l.name
            self.where += '</p>'
        else:
            self.where = ''

        # description
        self.desc = '<p><b>Description:</b> ' + self.event.description[:100]
        self.desc += ('...</p>' if len(self.event.description) > 100
                      else '</p>')

        self.event_url = self.event.get_absolute_url()  # url
        t = LEGACY_CALENDAR_TIME_FORMAT if self.event.l_start_date.minute else LEGACY_CALENDAR_HOUR_FORMAT
        self.title2 = (self.event.l_start_date.strftime(t).lstrip('0') +
                       ' ' + self.title)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        super(EventCalendar, self).formatday(day, weekday)
        now = get_now()
        self.day = day
        out = ''

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif now.month == self.mo and now.year == self.yr and day == now.day:
            if day in self.count:
                # don't return just yet
                out = self.wkday_today + self.anch
            else:
                return self.wkday_today + self.anch + self.end
        elif day in self.count:
            # don't return just yet
            out = self.wkday_not_today + self.anch
        else:
            return self.wkday_not_today + self.anch + self.end

        detail = "%s%s%s<br><a href='%s'>View details</a>"
        extras = ('<div title="%s" data-content="%s" data-container="body"'
                  ' data-toggle="popover" class="calendar-event"%s>')
        common = ' style=background:%s;color:%s;'

        # inject style and extras into calendar html
        for item in self.count[day]:
            self.pk = item[1]
            self.title = item[0]
            for event in self.events:
                if event.pk == self.pk:
                    self.event = event
                    self.check_if_cancelled()
                    # self.add_occurrence
                    self.popover_helper()
                    bg, fnt = self.event.get_colors()
            out += ('<a class="event-anch" href="' + self.event_url + '">' +
                    extras % (
                        self.title,
                        detail % (
                            self.when, self.where, self.desc, self.event_url
                        ),
                        common % (bg, fnt)
                    ) +
                    self.title2 + '</div></a>')

        return out + self.end


class LegacyMiniEventCalendar(LegacyGenericCalendar):
    def __init__(self, *args):
        super(MiniEventCalendar, self).__init__(*args)
        # Change count from a defaultdict to a regular dict, so that when we
        # try and check if there are days in count, they won't be added if they
        # aren't there.
        self.count = dict(self.count)

    def popover_helper(self):
        num_events = len(self.count[self.day])
        titles = ''
        for item in self.count[self.day]:
            pk = item[1]
            for event in self.events:
                if event.pk == pk:
                    self.event = event
                    t = LEGACY_CALENDAR_TIME_FORMAT if event.l_start_date.minute else LEGACY_CALENDAR_HOUR_FORMAT
                    self.title = event.l_start_date.strftime(t).lstrip('0') + \
                        ' - ' + event.title
                    self.check_if_cancelled()
                    titles += "<li><a href=\'%s\'>%s</a></li>" % (
                        event.get_absolute_url(), self.title
                    )
        self.cal_event = '<div data-content="<ul>%s</ul>"\
            data-container="body"\
            data-toggle="popover" class="calendar-event">%s</div>' % (
            titles, num_events)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        super(MiniEventCalendar, self).formatday(day, weekday)
        now = get_now()
        self.day = day

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif now.month == self.mo and now.year == self.yr and day == now.day:
            if day in self.count:
                self.popover_helper()
                return self.wkday_today + self.anch + self.cal_event + self.end
            else:
                return self.wkday_today + self.anch + self.end
        elif day in self.count:
            self.popover_helper()
            return self.wkday_not_today + self.anch + self.cal_event + self.end
        else:
            return self.wkday_not_today + self.anch + self.end
