from __future__ import unicode_literals

from calendar import LocaleHTMLCalendar, month_name

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

    def popover_helper(self, day, event, pk, title):
        """Returns variables used to build popovers."""
        when = ('<p><b>When:</b> ' + month_name[self.mo] + ' ' +
                str(day) + ', ' + event.l_start_date.strftime(
                    "%I:%M%p").lstrip('0') + ' - ' +
                event.l_end_date.strftime("%I:%M%p").lstrip('0') +
                '</p>')

        where = '<p><b>Where:</b> '
        for l in event.location.all():
            where += l.name
        if where == '<p><b>Where:</b> ':  # no location(s) added
            where = ''
        else:
            where += '</p>'

        desc = '<p><b>Description:</b> ' + event.description[:100]
        desc += ('...</p>' if len(event.description) > 100
                 else '</p>')

        event_url = event.get_absolute_url()
        t = "%I:%M%p" if event.l_start_date.minute else "%I%p"
        title2 = (event.l_start_date.strftime(t).lstrip('0') +
                  ' ' + title)
        return when, where, desc, event_url, title2

    def formatday(self, day, weekday):
        """Return a day as a table cell."""

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
            pk = item[1]
            title = item[0]
            for event in self.events:
                if event.pk == pk:
                    when, where, desc, event_url, title2 = self.popover_helper(
                        day, event, pk, title
                    )
                    bg, fnt = event.get_colors()
            out += ('<a class="event-anch" href="' + event_url + '">' +
                    extras % (
                        title,
                        detail % (when, where, desc, event_url),
                        common % (bg, fnt)
                    ) +
                    title2 + '</div></a>')

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
    def __init__(self, year, month, count, *args):
        super(MiniEventCalendar, self).__init__(*args)
        self.yr = year
        self.mo = month
        self.count = dict(count)

    def formatday(self, day, weekday):
        """Return a day as a table cell."""
        wkday_not_today = '<td class="%s"><div class="td-inner">' % (
            self.cssclasses[weekday])

        wkday_today = (
            '<td class="%s calendar-today"><div class="td-inner">' % (
                self.cssclasses[weekday])
        )

        anch = '<a href="/%s/%d/%d/%d">%d</a>' % (
            URL, self.yr, self.mo, day, day
        )

        try:
            cal_event = '<div data-content="<ul></ul>" data-container="body"\
                data-toggle="popover" class="calendar-event">%s</div>' % (
                len(self.count[day]))
        except KeyError:  # no events this day
            pass

        end = '</div></td>'

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif now.month == self.mo and now.year == self.yr and day == now.day:
            if day in self.count:
                return wkday_today + anch + cal_event + end
            else:
                return wkday_today + anch + end
        elif day in self.count:
            return wkday_not_today + anch + cal_event + end
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
