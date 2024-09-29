# -*- coding: utf-8 -*-
import argparse
import logging
import os
import random
import signal
import sys
import time


logger = logging.getLogger('main')
TERMINATE = False


def get_parser():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0, dest='verbosity',
        help='Increase verbosity level by one for every "v" '
             '(default: %(default)s)')

    return parser


def sig_handler(sig_num, stack_frame):
    del stack_frame
    global TERMINATE

    logger.debug('Got signal %d', sig_num)
    TERMINATE = True


def main(opts):
    del opts

    if os.getenv('DISABLE_SIGNAL_HANDLER', 'false').lower() != 'true':
        signal.signal(signal.SIGTERM, sig_handler)

    delay = random.randint(0, 60)
    with open('/tmp/startup.txt', 'w', encoding='utf-8') as f:
        f.write(str(time.time()))
    with open('/tmp/delay.txt', 'w', encoding='utf-8') as f:
        f.write(str(delay))
    logger.info('Unhealthy in %d seconds', delay)

    while not TERMINATE:
        time.sleep(3)


if __name__ == '__main__':
    options = get_parser().parse_args()
    levels = [logging.DEBUG, logging.INFO, logging.WARNING][::-1]
    verbosity = min([options.verbosity, len(levels)-1])
    logging.basicConfig(level=levels[verbosity])
    if options.verbosity <= len(levels)-1:
        for l in ('library_01',):
            logging.getLogger(l).setLevel(logging.WARNING)
    logger.debug('Starting')
    sys.exit(main(options) or 0)
