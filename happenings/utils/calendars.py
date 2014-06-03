from __future__ import unicode_literals

from calendar import LocaleHTMLCalendar, month_name
from datetime import date

from django.conf import settings

from .common import now

URL = getattr(settings, "CALENDAR_URL", 'calendar')


class EventCalendar(LocaleHTMLCalendar):
    def __init__(self, year, month, count, all_month_events, *args):
        super(EventCalendar, self).__init__(*args)
        self.yr = year
        self.mo = month
        self.count = count  # defaultdict in {date:[title1, title2,]} format
        self.events = all_month_events

    def add_occurrence(self):
        try:
            self.event.occurrence.append(self.day)
        except AttributeError:
            self.event.occurrence = []
            self.event.occurrence.append(self.day)

    def check_if_cancelled(self):
        if self.event.cancellations.count():
            cancellations = self.event.cancellations.all()
            d = date(self.yr, self.mo, self.day)
            for cancellation in cancellations:
                if cancellation.date == d:
                    self.title += " (CANCELLED)"

    def popover_helper(self):
        """Returns variables used to build popovers."""
        self.when = ('<p><b>When:</b> ' + month_name[self.mo] + ' ' +
                     str(self.day) + ', ' + self.event.l_start_date.strftime(
                         "%I:%M%p").lstrip('0') + ' - ' +
                     self.event.l_end_date.strftime("%I:%M%p").lstrip('0') +
                     '</p>')

        if self.event.location.count():
            self.where = '<p><b>Where:</b> '
            for l in self.event.location.all():
                self.where += l.name
            self.where += '</p>'
        else:
            self.where = ''

        self.desc = '<p><b>Description:</b> ' + self.event.description[:100]
        self.desc += ('...</p>' if len(self.event.description) > 100
                      else '</p>')

        self.event_url = self.event.get_absolute_url()
        t = "%I:%M%p" if self.event.l_start_date.minute else "%I%p"
        self.title2 = (self.event.l_start_date.strftime(t).lstrip('0') +
                       ' ' + self.title)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        self.day = day

        wkday_not_today = ('<td class="%s"><div class="td-inner">'
                           % self.cssclasses[weekday])

        wkday_today = ('<td class="%s calendar-today"><div class="td-inner">'
                       % self.cssclasses[weekday])

        end = '</div></td>'

        anch = '<a href="/%s/%d/%d/%d/">%d</a>' % (
            URL, self.yr, self.mo, day, day
        )

        out = ''

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif now.month == self.mo and now.year == self.yr and day == now.day:
            if day in self.count:
                # don't return just yet
                out = wkday_today + anch
            else:
                return wkday_today + anch + end
        elif day in self.count:
            # don't return just yet
            out = wkday_not_today + anch
        else:
            return wkday_not_today + anch + end

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
                    self.add_occurrence
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

        return out + end

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Change colspan to "5", add "today" button, and return a month
        name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return ('<tr><th colspan="5" class="month">'
                '<button id="cal-today-btn" class="btn btn-small">'
                'Today</button> %s</th></tr>' % s)


class MiniEventCalendar(LocaleHTMLCalendar):
    def __init__(self, year, month, count, events, *args):
        super(MiniEventCalendar, self).__init__(*args)
        self.yr = year
        self.mo = month
        self.count = dict(count)
        self.events = events

    def add_occurrence(self):
        try:
            self.event.occurrence.append(self.day)
        except AttributeError:
            self.event.occurrence = []
            self.event.occurrence.append(self.day)

    def check_if_cancelled(self):
        if self.event.cancellations.count():
            cancellations = self.event.cancellations.all()
            d = date(self.yr, self.mo, self.day)
            for cancellation in cancellations:
                if cancellation.date == d:
                    self.title += " (CANCELLED)"

    def popover_helper(self):
        num_events = len(self.count[self.day])
        titles = ''
        for item in self.count[self.day]:
            pk = item[1]
            for event in self.events:
                if event.pk == pk:
                    self.event = event
                    t = "%I:%M%p" if event.l_start_date.minute else "%I%p"
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
        self.day = day
        wkday_not_today = '<td class="%s"><div class="td-inner">' % (
            self.cssclasses[weekday])

        wkday_today = (
            '<td class="%s calendar-today"><div class="td-inner">' % (
                self.cssclasses[weekday])
        )

        anch = '<a href="/%s/%d/%d/%d">%d</a>' % (
            URL, self.yr, self.mo, day, day
        )

        end = '</div></td>'

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif now.month == self.mo and now.year == self.yr and day == now.day:
            if day in self.count:
                self.popover_helper()
                return wkday_today + anch + self.cal_event + end
            else:
                return wkday_today + anch + end
        elif day in self.count:
            self.popover_helper()
            return wkday_not_today + anch + self.cal_event + end
        else:
            return wkday_not_today + anch + end

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Change colspan to "5", add "today" button, and return a month
        name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return ('<tr><th colspan="5" class="month">'
                '<button id="cal-today-btn" class="btn btn-small">'
                'Today</button> %s</th></tr>' % s)
