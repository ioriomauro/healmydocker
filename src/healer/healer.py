# -*- coding: utf-8 -*-
import logging
import pprint
import signal
import threading
import time

from datetime import datetime, timezone
from enum import StrEnum
from typing import TYPE_CHECKING
from queue import Empty, Queue

import docker
import docker.errors
if TYPE_CHECKING:
    import docker.types

from . import LABEL


logger = logging.getLogger(__name__)

PING_INTERVAL = 30  # Seconds
RESPONSIVENESS = 3  # Seconds


class ResurrectionQueue(threading.Thread):
    def __init__(self):
        super().__init__()
        self.event_queue = Queue()
        self.event_ids = set()
        self._terminate = False
        self.client = docker.from_env()

    def __len__(self):
        return self.event_queue.qsize()

    def terminate(self):
        self._terminate = True

    def append(self, event_info):
        logger.debug('Add new resurrection event')
        container_id = event_info['id']
        if container_id in self.event_ids:
            logger.info('Skipping duplicated (too fast?) id: %r', container_id)
            return

        logger.info('Got new resurrection event for id %s. Queue len was %d',
                    container_id, len(self))
        self.event_ids.add(container_id)
        self.event_queue.put(event_info)

    def run(self):
        logger.info('Entering resurrection queue loop handler')
        while not self._terminate:
            try:
                event = self.event_queue.get(timeout=RESPONSIVENESS)
                logger.debug('Pop event from resurrection queue: %s',
                             pprint.pformat(event))

                self.resurrect(event)
            except Empty:
                time.sleep(RESPONSIVENESS)
        logger.info('Exiting resurrection queue loop handler')

    def resurrect(self, event):
        container_id = event['id']
        try:
            container = self.client.containers.get(container_id)
            logger.info('Restarting container %r', container_id)
            t1 = time.time()
            container.restart(timeout=15)
            container.reload()
            logger.info('Restarted container %r in %.2f seconds - status %r',
                        container_id, time.time() - t1, container.status)
        except docker.errors.NotFound:
            logger.error('Container id %r not found. Skipping resurrection',
                         container_id)
        self.event_ids.remove(container_id)


class Event:
    class TYPE(StrEnum):
        HEALTHY = 'healthy'
        UNHEALTHY = 'unhealthy'

    def __init__(self, data: dict):
        self._data = data

    @property
    def type(self):
        action: str = self._data.get('Action', ': ')
        if ': ' not in action:
            raise RuntimeError('Action is %r - unknown format', action)

        key, value = action.split(': ', 1)
        if key != 'health_status':
            raise RuntimeError('Event is %r - not "health_status"', key)
        # pylint: disable=E1101
        assert value in (Event.TYPE.HEALTHY.value, Event.TYPE.UNHEALTHY.value), value
        return Event.TYPE.HEALTHY if value == 'healthy' else Event.TYPE.UNHEALTHY


class Healer:
    def __init__(self):
        self.client = c = docker.from_env()
        self.docker_info = c.info()
        self.docker_version = c.version()
        self.events: docker.types.daemon.CancellableStream = None
        self._terminate = False
        self.loop_thread = threading.Thread(target=self.loop)
        self.ping_thread = threading.Thread(target=self.ping)
        self.resurrect = ResurrectionQueue()
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGUSR1, self.sigusr1_handler)

    def terminate(self):
        if self.events is not None:
            self.events.close()
        self._terminate = True
        self.resurrect.terminate()

    def loop(self):
        event_filters = {
            'event': 'health_status',
            'label': f'{LABEL}=true',
        }
        logger.info('Entering docker events loop handler')
        while not self._terminate:
            since = datetime.now(timezone.utc)
            logger.debug('since: %s', since)
            self.events = self.client.events(
                decode=True,
                filters=event_filters,
                since=since)
            logger.debug('loop before')
            try:
                for event in self.events:
                    logger.debug(pprint.pformat(event))
                    if Event(event).type == Event.TYPE.HEALTHY:
                        logger.debug('Ignoring healthy event')
                        continue
                    self.resurrect.append(event)
            except:
                logger.exception('events error')
                raise
            logger.debug('loop after')
        logger.info('Exiting docker events loop handler')

    def sigterm_handler(self, sig_num, stack_frame):
        del stack_frame
        logger.info('Got signal %d', sig_num)
        self.terminate()

    def sigusr1_handler(self, sig_num, stack_frame):
        del stack_frame
        logger.debug('Got signal %d', sig_num)
        status = {
            'docker_ping': self.client.ping(),
            # 'docker_info': self.docker_info,
            'docker_version': self.docker_version,
            'date_utc': datetime.now(timezone.utc).isoformat(),
            'resurrection_queue_len': len(self.resurrect),
        }
        logger.warning('Status: %s', pprint.pformat(status))

    def run(self):
        self.loop_thread.start()
        self.ping_thread.start()
        self.resurrect.start()

        while not self._terminate:
            time.sleep(RESPONSIVENESS)
        self.loop_thread.join()
        self.ping_thread.join()
        self.resurrect.join()

        self.client.close()
        logger.info('Quit')

    def ping(self):
        try:
            t = time.time()
            logger.info('Entering docker ping loop handler')
            while not self._terminate:
                time.sleep(RESPONSIVENESS)
                if (time.time() - t) > PING_INTERVAL:
                    pong = self.client.ping()
                    logger.debug('Docker ping response: %r', pong)
                    if not pong:
                        logger.error('Docker ping is %r. Hmmm...', pong)
                    t = time.time()
            logger.info('Exiting docker ping loop handler')
        except:
            logger.exception('Docker ping')
