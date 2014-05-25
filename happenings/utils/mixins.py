from __future__ import unicode_literals

from datetime import datetime
from json import dumps, loads

from django.http import HttpResponse
from django.core import serializers


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response. See:
    https://docs.djangoproject.com/en/dev/topics/class-based-views/mixins/
    """
    def render_to_json_response(self, context, **kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            **kwargs
        )

    def convert_context_to_json(self, context):
        """
        Get what we want out of the context dict and convert that to a JSON
        object. Note that this does no object serialization b/c we're
        not sending any objects.
        """
        if 'month/shift' in self.request.path:  # month calendar
            return dumps(self.get_month_calendar_dict(context))
        elif 'event-list/shift' in self.request.path:  # month event list
            return dumps(self.get_month_event_list_dict(context))
        elif 'cal-and-list/shift' in self.request.path:
            cal = self.get_month_calendar_dict(context)
            l = self.get_month_event_list_dict(context)
            cal.update(l)
            return dumps(cal)
        else:  # day list view
            return dumps(self.get_day_context_dict(context))

    @staticmethod
    def get_month_calendar_dict(context):
        return dict(
            calendar=context['calendar'],
            month_and_year=context['month_and_year']
        )

    @staticmethod
    def get_month_event_list_dict(context):
        m = int(context['current']['month_num'])
        y = int(context['current']['year'])
        remove_these = (
            'all_day', 'description', 'categories', 'tags', 'created_by',
            'location',
        )

        for k, v in context['events'].items():
            context['events'][k] = loads(serializers.serialize("json", v))
            for event in context['events'][k]:
                # remove unnec. fields to shorten the json response
                for item in remove_these:
                    del event['fields'][item]
                event['weekday'] = datetime(  # add weekday e.g Fri, Mon, etc.
                    y, m, k).strftime("%A")[:3]
        return dict(
            month=context['current']['month'], events=context['events']
        )

    @staticmethod
    def get_day_context_dict(context):
        events = loads(serializers.serialize("json", context['events']))
        return dict(
            events=events,
            year=context['year'],
            month=context['month_num'],
            month_name=context['month'],
            day=context['day'],
            nxt=context['next'],
            prev=context['prev'],
        )
