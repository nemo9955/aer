from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.component.component import entrypoint

# pylint: disable=I0011,E1129


def init(parent_parser):
    contParser = parent_parser.add_parser(
        'cont', help='Container commands to run on every host ',
        conflict_handler='resolve')

    contParser.set_defaults(entrypoint=entrypoint)
    contParser.add_argument('-c', "--containers", dest="containers",
                            nargs="+", metavar="c", help='Select containers')
    action_group = contParser.add_argument_group("Actions")
    action_group.add_argument("-d", "--deploy", dest="deploy",
                              action="store_true", help='Deploy containers to hosts')

    target_group = contParser.add_argument_group("Targeting")
    # target_group.add_argument('-a', "--alias-config", dest="alias_config",
    #                           help='Select config from alias')
    target_group.add_argument('-t', "--target-host", dest="target_host",
                              help='Specify exact host to deploy the containers to.')

    # action_group.add_argument("-b", "--backup", dest="backup",
    #                           action="store_true", help='Backup containers data ')
    # action_group.add_argument("-e", "--export", dest="export",
    #                           action="store_true", help='Export in human-frendly format')
    # action_group.add_argument("-r", "--restore", dest="restore",
    # action="store_true", help='Restore container data')
