from __future__ import unicode_literals

import datetime

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible

from .managers import EventManager

auth_user_model = getattr(settings, "AUTH_USER_MODEL", "auth.User")


@python_2_unicode_compatible
class Event(models.Model):

    USER_COLORS = getattr(settings, "CALENDAR_COLORS", '')

    REPEAT_CHOICES = (
        ('NEVER', _('Never')),
        ('DAILY', _('Every Day')),
        ('WEEKDAY', _('Every Weekday')),
        ('WEEKLY', _('Every Week')),
        ('BIWEEKLY', _('Every 2 Weeks')),
        ('MONTHLY', _('Every Month')),
        ('YEARLY', _('Every Year')),
    )
    COLORS = [
        ('eeeeee', _('gray')),
        ('ff0000', _('red')),
        ('0000ff', _('blue')),
        ('00ff00', _('green')),
        ('000000', _('black')),
        ('ffffff', _('white')),
    ]

    try:
        COLORS += USER_COLORS
    except Exception:
        pass

    start_date = models.DateTimeField(verbose_name=_("start date"))
    end_date = models.DateTimeField(_("end date"))
    all_day = models.BooleanField(_("all day"))
    repeat = models.CharField(
        _("repeat"), max_length=15, choices=REPEAT_CHOICES, default='NEVER'
    )
    end_repeat = models.DateField(_("end repeat"), null=True, blank=True)
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    location = models.ManyToManyField(
        'Location', verbose_name=_('locations'), blank=True
    )
    objects = EventManager()
    created_by = models.ForeignKey(
        auth_user_model, verbose_name=_("created by"), related_name='events'
    )
    categories = models.ManyToManyField(
        'Category', verbose_name=_('categories'), blank=True
    )
    tags = models.ManyToManyField('Tag', verbose_name=_('tags'), blank=True)

    # --------------------------------COLORS-------------------------------- #
    background_color = models.CharField(
        _("background color"), max_length=10, choices=COLORS, default='eeeeee'
    )
    background_color_custom = models.CharField(
        _("background color custom"), max_length=6, blank=True,
        help_text=_('Must be a valid hex triplet. Default is gray (eeeeee)')
    )
    font_color = models.CharField(
        _("font color"), max_length=10, choices=COLORS, default='000000'
    )
    font_color_custom = models.CharField(
        _("font color custom"), max_length=6, blank=True,
        help_text=_('Must be a valid hex triplet. Default is black (000000)')
    )

    @property
    def l_start_date(self):
        """Localized start date."""
        return timezone.localtime(self.start_date)

    @property
    def l_end_date(self):
        """Localized end date."""
        return timezone.localtime(self.end_date)

    def repeats(self, repeat):
        return True if self.repeat == repeat else False

    def is_chunk(self):
        return True if self.l_start_date.day != self.l_end_date.day else False

    def starts_same_month_as(self, month):
        return True if self.l_start_date.month == month else False

    def ends_same_month_as(self, month):
        return True if self.l_end_date.month == month else False

    def starts_same_year_month_as(self, year, month):
        if self.l_start_date.year == year and self.l_start_date.month == month:
            return True
        else:
            return False

    def starts_same_month_not_year_as(self, month, year):
        if self.l_start_date.year != year and self.l_start_date.month == month:
            return True
        else:
            return False

    def starts_ends_same_month(self):
        return (True if self.l_start_date.month == self.l_end_date.month
                else False)

    def start_end_diff(self):
        """Return the difference between start and end dates."""
        s = self.l_start_date
        e = self.l_end_date
        start = datetime.date(s.year, s.month, s.day)
        end = datetime.date(e.year, e.month, e.day)
        diff = start - end
        return abs(diff.days)

    def get_colors(self):
        bg = self.background_color_custom
        fnt = self.font_color_custom
        if not bg:
            bg = self.background_color
        if not fnt:
            fnt = self.font_color
        bg = '#' + bg
        fnt = '#' + fnt
        return bg, fnt

    def will_occur(self, now):
        """Returns True if the event will occur again after 'now'."""
        if self.end_repeat is None or self.end_repeat >= now.date() or \
                self.l_start_date >= now or self.l_end_date >= now:
            return True
        else:
            return False

    def __str__(self):
        return self.title

    def clean(self):
        self.clean_start_end_dates()
        self.clean_repeat()
        self.clean_colors()

    def clean_start_end_dates(self):
        if self.start_date and self.end_date:
            if self.l_start_date > self.l_end_date:
                raise ValidationError(
                    "The event's start date must be before the end date."
                )
            elif (self.l_end_date - self.l_start_date) > datetime.timedelta(7):
                raise ValidationError(
                    "Only events spanning 7 days or less are supported."
                )

    def clean_repeat(self):
        if self.repeats('NEVER') and self.end_repeat:
            # events not scheduled to repeat should't have an end repeat date
            self.end_repeat = None

        if self.repeats('DAILY') or self.repeats('WEEKDAY'):
            if self.is_chunk():
                raise ValidationError(
                    "Repeating every day or every weekday is not supported \
                    for events that start and end on different days."
                )

    def clean_colors(self):
        """Makes sure that if a custom color is supplied, it's valid."""
        err = _("Color must be a valid hex triplet.")
        colors = ['background_color_custom', 'font_color_custom']
        colors2 = colors + ['background_color', 'font_color']
        # If there are custom colors specified in settings, length of
        # self.COLORS will be > 6, so check for validity
        if len(self.COLORS) > 6:
            colors = colors2
        for color in colors:
            c = getattr(self, color)
            l = len(c)
            if l:
                if l != 6:
                    raise ValidationError(err)
                else:
                    try:
                        int(c, 16)
                    except ValueError:
                        raise ValidationError(err)

    def get_absolute_url(self):
        return reverse('calendar:detail', args=[str(self.id)])

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')


@python_2_unicode_compatible
class Location(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    address_line_1 = models.CharField(
        _('Address Line 1'), max_length=255, blank=True)
    address_line_2 = models.CharField(
        _('Address Line 2'), max_length=255, blank=True)
    address_line_3 = models.CharField(
        _('Address Line 3'), max_length=255, blank=True)
    state = models.CharField(
        _('State / Province / Region'), max_length=63, blank=True)
    city = models.CharField(
        _('City / Town'), max_length=63, blank=True)
    zipcode = models.CharField(
        _('ZIP / Postal Code'), max_length=31, blank=True)
    country = models.CharField(_('Country'), max_length=127, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Category(models.Model):
    title = models.CharField(_('title'), max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(_('name'), max_length=255)

    def __str__(self):
        return self.name
