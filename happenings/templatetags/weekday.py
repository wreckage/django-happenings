from __future__ import unicode_literals

from datetime import date
from calendar import day_name
from django.template import Library, TemplateSyntaxError
from django.utils.dates import WEEKDAYS_ABBR, WEEKDAYS

register = Library()


@register.simple_tag
def weekday(year_or_num, month=None, day=None, full=False):
    """Simple tag - returns the weekday of the given (year, month, day) or of given (weekday_number).

    Usage (in template):

    {% weekday 2014 3 3 %}

    Result: Mon

    Return abbreviation by default. To return full name: pass full=True

    {% weekday 2014 3 3 full=True %}

    Result: Monday


    When only number of weekday is given then 0 is considered as "Monday"

    {% weekday 0 full=True %}

    Result: Monday

    """
    if any([month, day]) and not all([month, day]):
        raise TemplateSyntaxError("weekday accepts 1 or 3 arguments plus optional 'full' argument")

    try:
        if all([year_or_num, month, day]):
            weekday_num = date(*map(int, (year_or_num, month, day))).weekday()
        else:
            weekday_num = year_or_num
        if full:
            return WEEKDAYS[weekday_num]
        else:
            return WEEKDAYS_ABBR[weekday_num]
    except Exception:
        return


@register.filter
def weekday_css_class(weekday_num, calendar):
    return calendar.cssclasses[weekday_num]
