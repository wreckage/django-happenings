from __future__ import unicode_literals

import datetime
from itertools import chain
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

    def repeat(self, year, month, category=None, tag=None):
        """
        Returns events that repeat, and that should be displayed on the
        calendar month. Yearly repeating events are handled separately b/c
        they're the only ones that don't appear on every month before their
        end_repeat date.
        """
        kwargs = self._get_kwargs(category, tag)
        ym_first = make_aware(
            datetime.datetime(year, month, 1),
            get_default_timezone()
        )
        ym_last = make_aware(
            datetime.datetime(year, month, monthrange(year, month)[1]),
            get_default_timezone()
        )

        # without yearly repeat
        a = self.model.objects.exclude(
            Q(repeat="NEVER") | Q(repeat="YEARLY")
        ).filter(
            # only events that are still repeating
            Q(end_repeat=None) | Q(end_repeat__gte=ym_first),
            start_date__lte=ym_last  # no events that haven't started yet
        ).filter(**kwargs).prefetch_related('location')

        # with yearly repeat
        b = self.model.objects.filter(
            Q(start_date__month=month) | Q(end_date__month=month),
            Q(end_repeat=None) | Q(end_repeat__gte=ym_first),
            repeat="YEARLY", start_date__lte=ym_last
        ).filter(**kwargs).prefetch_related('location')

        # chain them together and return the set. The querysets will be
        # evaluated at this point.
        return set(chain(a, b))

    def month_events(self, year, month, category=None, tag=None):
        """
        Returns the events within the given month and year. If category
        and/or tag is given, the events returned will have
        those categories/tags.
        """
        kwargs = self._get_kwargs(category, tag)
        return self.model.objects.within(year, month).filter(
            **kwargs).prefetch_related('location')

    def within(self, year, month):
        """Returns events within the given year and month."""
        return self.model.objects.filter(
            Q(start_date__year=year) | Q(end_date__year=year),
            Q(start_date__month=month) | Q(end_date__month=month)
        )

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
        )
