from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from happenings.utils.common import get_net


class GetNetTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse('calendar:list')

    def test_valid_next(self):
        url = self.url + '?cal_next=1'
        req = self.factory.get(url)
        net = get_net(req)
        self.assertEqual(net, 1)

    def test_valid_prev(self):
        url = self.url + '?cal_prev=1'
        req = self.factory.get(url)
        net = get_net(req)
        self.assertEqual(net, -1)

    def test_invalid(self):
        url = self.url + '?cal_next=nann'
        req = self.factory.get(url)
        net = get_net(req)
        self.assertEqual(net, 0)

    def test_valid_next_and_prev(self):
        url = self.url + '?cal_next=1&cal_prev=2'
        req = self.factory.get(url)
        net = get_net(req)
        self.assertEqual(net, -1)
