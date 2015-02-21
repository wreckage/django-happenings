from __future__ import unicode_literals

import datetime
from calendar import monthrange

from django.db import models
from django.db.models import Q
from django.utils.timezone import make_aware, get_default_timezone


class EventManager(models.Manager):
    def _get_kwargs(self, category, tag):
        """Helper function for getting category/tag kwargs."""
        vals = {
            'categories__title__iexact': category,
            'tags__name__iexact': tag
        }
        kwargs = {}
        for k, v in vals.items():
            if v:
                kwargs[k] = v
        return kwargs

    @staticmethod
    def get_first_and_last(year, month):
        """Returns two datetimes: first day and last day of given year&month"""
        ym_first = make_aware(
            datetime.datetime(year, month, 1),
            get_default_timezone()
        )
        ym_last = make_aware(
            datetime.datetime(year, month, monthrange(year, month)[1], 23, 59, 59, 1000000-1),
            get_default_timezone()
        )
        return ym_first, ym_last

    def all_month_events(self, year, month, category=None, tag=None,
                         loc=False, cncl=False):
        """
        Returns all events that have an occurrence within the given
        month & year.
        """
        kwargs = self._get_kwargs(category, tag)
        ym_first, ym_last = self.get_first_and_last(year, month)

        pref = []
        if loc:
            pref.append("location")
        if cncl:
            pref.append("cancellations")

        # for yearly repeat, we need to check the start and end date months
        # b/c yearly events should occur every year in the same month
        r = Q(repeat="YEARLY")
        dstart_mo = Q(start_date__month=month)
        dend_mo = Q(end_date__month=month)

        dstart_yr = Q(start_date__year=year)
        dend_yr = Q(end_date__year=year)

        return self.model.objects.filter(
            # only events that are still repeating
            r & (dstart_mo | dend_mo) |  # yearly repeat
            (~Q(repeat="NEVER")) |  # all other repeats
            ((dstart_yr | dend_yr) & (dstart_mo | dend_yr)),  # non-repeating
            Q(end_repeat=None) | Q(end_repeat__gte=ym_first),
            start_date__lte=ym_last  # no events that haven't started yet
        ).filter(**kwargs).prefetch_related(*pref).distinct()

#    XXX These are no longer used since all_month_events() (above) was created.
#    def month_events(self, year, month, category=None, tag=None):
#        """
#        Returns the events within the given month and year. If category
#        and/or tag is given, the events returned will have
#        those categories/tags.
#        """
#        kwargs = self._get_kwargs(category, tag)
#        return self.model.objects.within(year, month).filter(
#            **kwargs).prefetch_related('location', 'cancellations')
#
#    def within(self, year, month):
#        """Returns events within the given year and month."""
#        return self.model.objects.filter(
#            Q(start_date__year=year) | Q(end_date__year=year),
#            Q(start_date__month=month) | Q(end_date__month=month)
#        )

    def live(self, now):
        """
        Returns a queryset of events that will occur again after 'now'.
        Used to help generate a list of upcoming events.
        """
        return self.model.objects.filter(
            Q(end_repeat=None) | Q(end_repeat__gte=now) |
            Q(start_date__gte=now) | Q(end_date__gte=now)
        ).exclude(  # exclude single day events that won't occur again
            start_date__lt=now, end_date__lt=now,
            repeat="NEVER", end_repeat=None,
        ).prefetch_related('cancellations')
