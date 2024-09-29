# -*- coding: utf-8 -*-
import argparse
import logging
import sys

from datetime import datetime, timedelta, timezone


logger = logging.getLogger('main')


def get_parser():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0, dest='verbosity',
        help='Increase verbosity level by one for every "v" '
             '(default: %(default)s)')

    return parser


def main(opts):
    del opts
    with open('/tmp/startup.txt', 'r', encoding='utf-8') as f:
        startup = datetime.fromtimestamp(float(f.read()), timezone.utc)
    with open('/tmp/delay.txt', 'r', encoding='utf-8') as f:
        delay = timedelta(seconds=int(f.read()))
    now = datetime.now(timezone.utc)

    sys.exit(
        1 if startup + delay < now else 0
    )


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
