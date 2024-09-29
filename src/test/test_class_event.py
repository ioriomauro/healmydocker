# -*- coding: utf-8 -*-
import unittest

from healer.healer import Event


class TestEventClass(unittest.TestCase):
    def test_type_healthy(self):
        e = Event({
            'Action': 'health_status: healthy'
        })

        self.assertEqual(e.type, Event.TYPE.HEALTHY)

    def test_type_unhealthy(self):
        e = Event({
            'Action': 'health_status: unhealthy'
        })

        self.assertEqual(e.type, Event.TYPE.UNHEALTHY)

    def test_type_empty(self):
        self.assertRaises(RuntimeError, getattr, Event({}), 'type')
        self.assertRaises(RuntimeError, getattr, Event({
            "Action": "start"
        }), 'type')
        self.assertRaises(RuntimeError, getattr, Event({
            "Action": "another: false"
        }), 'type')
