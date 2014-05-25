from __future__ import unicode_literals

from django.test import TestCase

from happenings.utils.common import get_next_and_prev


class GetNextAndPrevTest(TestCase):
    def test_net_zero(self):
        net = 0
        nxt, prev = get_next_and_prev(net)
        self.assertEqual(nxt, 1)
        self.assertEqual(prev, 1)

    def test_neg_net(self):
        net = -3
        nxt, prev = get_next_and_prev(net)
        self.assertEqual(nxt, -2)
        self.assertEqual(prev, 4)

    def test_pos_net(self):
        net = 3
        nxt, prev = get_next_and_prev(net)
        self.assertEqual(nxt, 4)
        self.assertEqual(prev, -2)
