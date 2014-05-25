from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from .event_factory import create_event


HTML = 'class="calendar-event"'


class EventListViewCategoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            'foo', 'bar@example.com', 'secret'
        )
        self.event = create_event(
            created_by=self.user,
            title="Smith",
            description="Just an event.",
            categories=["foo"]
        )
        self.event2 = create_event(
            created_by=self.user,
            title="Alison",
            description="Just an event.",
            categories=["bar"],
            repeat="YEARLY"
        )
        self.event3 = create_event(
            created_by=self.user,
            title="Tempz",
            description="Another one"
        )

    def test_list_view_event_with_category(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_category': 'foo'}
        )
        self.assertContains(response, self.event.title)
        self.assertNotContains(response, self.event2.title)
        self.assertNotContains(response, self.event3.title)
        self.assertContains(response, HTML)

    def test_list_view_event_with_category_on_repeating_event(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_category': 'bar'}
        )
        self.assertContains(response, self.event2.title)
        self.assertNotContains(response, self.event.title)
        self.assertNotContains(response, self.event3.title)
        self.assertContains(response, HTML)

    def test_list_view_event_with_category_on_repeating_event_next_year(self):
        response = self.client.get(
            reverse('calendar:list'), {'cal_category': 'bar', 'cal_next': 12}
        )
        self.assertContains(response, self.event2.title)
        self.assertNotContains(response, self.event.title)
        self.assertNotContains(response, self.event3.title)
        self.assertContains(response, HTML)

#    def test_day_list_view_event_with_category(self):
#        response = self.client.get(
#            reverse('calendar:list'), {'cal_category': 'foo'}
#        )
#        self.assertContains(response, self.event.title)
#        self.assertNotContains(response, self.event2.title)
#        self.assertNotContains(response, self.event3.title)
#        self.assertContains(response, "class=calendar-event>1</div>")
