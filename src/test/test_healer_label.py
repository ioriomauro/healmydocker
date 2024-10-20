# -*- coding: utf-8 -*-
import importlib
import os
import threading
import time
import unittest

from unittest.mock import patch

import docker

import healer
import healer.healer


class FakeEvents:
    '''
        This sounds crap to me. I'm almost sure that there's a better
        approach using mocks...
    '''
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def close(self):
        return True
    def __iter__(self):
        return iter([])


class TestHealerLabelDefault(unittest.TestCase):
    def setUp(self) -> None:
        healer.healer.PING_INTERVAL = 0
        healer.healer.RESPONSIVENESS = 0

    @patch.object(docker.DockerClient, 'events')
    def test_label_default(self, mock_events):
        def _terminate():
            time.sleep(1)
            h.terminate()

        h = healer.healer.Healer()

        # Target healer class polls periodically for events, so it will receive
        # many copies of fake_events
        fake_events = FakeEvents()
        mock_events.return_value = fake_events

        t = threading.Thread(target=_terminate)
        t.start()
        h.run()
        t.join()

        event_filters = {
            'event': 'health_status',
            'label': 'healme=true',
        }
        for c in mock_events.call_args_list:
            a = c.args
            k = c.kwargs
            self.assertEqual(a, ())
            self.assertEqual(k['decode'], True)
            self.assertDictEqual(k['filters'], event_filters)

class TestHealerLabelCustom(unittest.TestCase):
    def setUp(self) -> None:
        os.environ['HMD_CONTAINER_LABEL'] = 'CUSTOM'
        importlib.reload(healer)
        importlib.reload(healer.healer)
        healer.healer.PING_INTERVAL = 0
        healer.healer.RESPONSIVENESS = 0

    def tearDown(self) -> None:
        os.environ['HMD_CONTAINER_LABEL'] = 'healme'
        importlib.reload(healer)
        importlib.reload(healer.healer)

    @patch.object(docker.DockerClient, 'events')
    def test_label_custom(self, mock_events):
        def _terminate():
            time.sleep(1)
            h.terminate()

        h = healer.healer.Healer()

        # Target healer class polls periodically for events, so it will receive
        # many copies of fake_events
        fake_events = FakeEvents()
        mock_events.return_value = fake_events

        t = threading.Thread(target=_terminate)
        t.start()
        h.run()
        t.join()

        event_filters = {
            'event': 'health_status',
            'label': 'CUSTOM=true',
        }
        for c in mock_events.call_args_list:
            a = c.args
            k = c.kwargs
            self.assertEqual(a, ())
            self.assertEqual(k['decode'], True)
            self.assertEqual(k['filters'], event_filters)
