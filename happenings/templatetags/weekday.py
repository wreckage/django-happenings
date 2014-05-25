from __future__ import unicode_literals

from datetime import date
from calendar import day_name
from django.template import Library

register = Library()


@register.simple_tag
def weekday(year, month, day):
    """
    Simple tag - returns the weekday of the given year, month, and day.
    Usage (in template):

    {% weekday 2014 3 3 %}

    Result: Mon
    """
    try:
        return day_name[date(*map(int, (year, month, day))).weekday()][:3]
    except Exception:
        return
