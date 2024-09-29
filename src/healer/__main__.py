import argparse
import logging
import sys

from .healer import Healer


logger = logging.getLogger('main')


def get_parser():
    parser = argparse.ArgumentParser(description='Docker Container Healer')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0, dest='verbosity',
        help='Increase verbosity level by one for every "v" '
             '(default: %(default)s)')

    return parser


def main(opts):
    del opts

    try:
        healer = Healer()
        healer.run()
    except:
        logger.exception('main')
        raise


if __name__ == '__main__':
    options = get_parser().parse_args()
    levels = [logging.DEBUG, logging.INFO, logging.WARNING][::-1]
    verbosity = min([options.verbosity, len(levels)-1])
    logging.basicConfig(level=levels[verbosity])
    if options.verbosity <= len(levels)-1:
        for l in ('urllib3',):
            logging.getLogger(l).setLevel(logging.WARNING)
    logger.info('Start')
    sys.exit(main(options) or 0)
