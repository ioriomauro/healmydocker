# -*- coding: utf-8 -*-
import logging
import threading
import time
import unittest

from unittest.mock import DEFAULT, MagicMock, patch

import docker
import docker.errors

from faker import Faker

from healer import healer


class TestHealer(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = Faker()

    @patch.object(docker.DockerClient, 'info')
    @patch.object(docker.DockerClient, 'version')
    def test_init(self, mock_version, mock_info):
        info_result = object()
        mock_info.return_value = info_result
        version_result = object()
        mock_version.return_value = version_result

        h = healer.Healer()
        self.assertIs(h.docker_info, info_result)
        self.assertIs(h.docker_version, version_result)

    @patch.object(docker.DockerClient, 'containers')
    @patch.object(docker.DockerClient, 'events')
    @patch.object(docker.DockerClient, 'ping')
    def test_run_w_missing_containerid(self, mock_ping, mock_events, mock_containers):
        healer.RESPONSIVENESS = 0
        healer.PING_INTERVAL = 0
        healer_logger = logging.getLogger('healer.healer')
        healer_logger.setLevel(logging.CRITICAL)

        mock_ping.return_value = True

        # health_status events are fake-generated, so container_id will not
        # be found. This will continuously raise docker.errors.NotFound
        # exception
        outer_fake = self.fake
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
                return iter([
                    {
                        'Action': f'health_status: {outer_fake.enum(healer.Event.TYPE).value}',
                        'id': outer_fake.pystr_format('#'*64, letters='0123456789abcdef'),
                    }
                    for _ in range(100)
                ])
        # Target healer class polls periodically for events, so it will receive
        # many copies of fake_events
        fake_events = FakeEvents()
        mock_events.return_value = fake_events

        called_with_id = []
        def _get(container_id):
            called_with_id.append(container_id)
            raise docker.errors.NotFound(
                message='This is for a test', explanation='This is for a test')
        mock_containers.get = _get

        def _terminate():
            time.sleep(3)
            h.terminate()

        h = healer.Healer()
        t = threading.Thread(target=_terminate)
        t.start()
        h.run()
        t.join()

        mock_ping.assert_called()
        mock_events.assert_called()
        # print(len(called_with_id))
