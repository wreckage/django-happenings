# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# python lib:
from calendar import LocaleHTMLCalendar, month_name
from datetime import date
import sys

# django:
from django.conf import settings

# thirdparties:
import six

# happenings:
from .common import now

URL = getattr(settings, "CALENDAR_URL", 'calendar')

CALENDAR_LOCALE = getattr(settings, 'CALENDAR_LOCALE', 'en_US.utf8')

CALENDAR_HOUR_FORMAT = CALENDAR_TIME_FORMAT = getattr(settings, 'CALENDAR_TIME_FORMAT', "%I:%M%p")


if '%p' in CALENDAR_TIME_FORMAT:
    CALENDAR_HOUR_FORMAT = CALENDAR_TIME_FORMAT.replace('%M', '')


class GenericCalendar(LocaleHTMLCalendar):
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
        self.count = count  # defaultdict in {date:[title1, title2,]} format
        self.events = all_month_events

#    def add_occurrence(self):
#        try:
#            self.event.occurrence.append(self.day)
#        except AttributeError:
#            self.event.occurrence = []
#            self.event.occurrence.append(self.day)

    def check_if_cancelled(self):
        if self.event.cancellations.count():
            cancellations = self.event.cancellations.all()
            d = date(self.yr, self.mo, self.day)
            for cancellation in cancellations:
                if cancellation.date == d:
                    self.title += " (CANCELLED)"

    def formatday(self, day, weekday):
        """Sets some commonly used variables."""
        self.wkday_not_today = '<td class="%s"><div class="td-inner">' % (
            self.cssclasses[weekday])

        self.wkday_today = (
            '<td class="%s calendar-today"><div class="td-inner">' % (
                self.cssclasses[weekday])
        )

        self.anch = '<a href="/%s/%d/%d/%d">%d</a>' % (
            URL, self.yr, self.mo, day, day
        )

        self.end = '</div></td>'

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


class EventCalendar(GenericCalendar):
    def popover_helper(self):
        """Returns variables used to build popovers."""
        # when
        display_month = month_name[self.mo]

        if isinstance(display_month, six.binary_type) and self.encoding:
            display_month = display_month.decode('utf-8')

        self.when = ('<p><b>When:</b> ' + display_month + ' ' +
                     str(self.day) + ', ' + self.event.l_start_date.strftime(
                         CALENDAR_TIME_FORMAT).lstrip('0') + ' - ' +
                     self.event.l_end_date.strftime(CALENDAR_TIME_FORMAT).lstrip('0') +
                     '</p>')

        if self.event.location.count():  # where
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
        t = CALENDAR_TIME_FORMAT if self.event.l_start_date.minute else CALENDAR_HOUR_FORMAT
        self.title2 = (self.event.l_start_date.strftime(t).lstrip('0') +
                       ' ' + self.title)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        super(EventCalendar, self).formatday(day, weekday)
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


class MiniEventCalendar(GenericCalendar):
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
                    t = CALENDAR_TIME_FORMAT if event.l_start_date.minute else CALENDAR_HOUR_FORMAT
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
