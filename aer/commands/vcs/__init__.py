from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.vcs.vcs import entrypoint

# pylint: disable=I0011,E1129


def init(parent_parser):
    from aer.commands import do

    doParser = parent_parser.add_parser(
        'vcs', help='Version control systems for easy interaction with needed repositories, be them yours or third party\'s  ', conflict_handler='resolve')  # add_help=False,
    doParser.set_defaults(entrypoint=entrypoint)

    group6 = doParser.add_argument_group("Enviroment management parameters")
    group6.add_argument("-LL", "--list-local-libs", action="store_true")
    group6.add_argument("-LLL", "--list-all-libs", action="store_true")
    group6.add_argument("-m", "--list-more-details", action="store_true")
    group6.add_argument("-u", "--libs-update", action="store_true", help="Also ensures libs are updated!")

    group6.add_argument("-e", "--libs-ensure",help="Ensure (if config and conditions allow) that the libs are available locally", action="store_true")
    group6.add_argument("-p", "--libs-push", action="store_true")
