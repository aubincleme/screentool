# Define a set of utility functions to initialize the environment
import argparse
import logging
import sys


def init_logger(logLevel):
    root = logging.getLogger()

    if (logLevel >= 1):
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[ %(levelname)s ] %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def parse_args():
    rootParser = argparse.ArgumentParser(prog='screentool',
                                         description='Provide a set of tools to manage X screen disposition')
    rootParser.add_argument('-v', '--verbose', action='count', default=0, help='enable verbose logs')

    subParsers = rootParser.add_subparsers(dest='action', required=True, help='the action to perform')

    subParsers.add_parser('list', help='list the registered layouts')
    subParsers.add_parser('configure', help='configure X on a registered layout')
    subParsers.add_parser('register', help='register the current screen layout')

    return rootParser.parse_args()
