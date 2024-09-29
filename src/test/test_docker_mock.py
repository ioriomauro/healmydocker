# -*- coding: utf-8 -*-
import unittest

from unittest.mock import patch

import docker


class TestDockerMock(unittest.TestCase):
    def test_mock_vanilla(self):
        c = docker.from_env()
        info = c.info()
        self.assertIsInstance(info, dict)

    def test_mock_list(self):
        c = docker.from_env()

        with patch('docker.DockerClient.info') as docker_info:
            docker_info.return_value = [123]

            info = c.info()
            self.assertIsInstance(info, list)
            self.assertEqual(info[0], 123)

        info = c.info()
        self.assertIsInstance(info, dict)

    def test_mock_events(self):
        c = docker.from_env()

        with patch('docker.DockerClient.events') as docker_events:
            docker_events.return_value = [{'a': 1}, {'a': 1}]

            for event in c.events():
                self.assertDictEqual(event, {'a': 1})

            docker_events.assert_called_once()
