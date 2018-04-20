from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.do.do import entrypoint

# pylint: disable=I0011,E1129


def init(parent_parser):
    from aer.commands import do

    doParser = parent_parser.add_parser(
        'do', help='Sub-command for general actions on localhost (dev) and hosts (prod) ', conflict_handler='resolve')  # add_help=False,
    doParser.set_defaults(entrypoint=entrypoint)

    target_group = doParser.add_argument_group("Targeting")
    # target_group.add_argument('-a', "--alias-config",
    #                           help='Select config from alias')
    target_group.add_argument('-t', "--target-host",
                              help='Specify exact host to deploy the containers to.')

    group1 = doParser.add_argument_group("Host/container actions")
    # group1.add_argument(
    #     "-e", "--ensure-env", action="store_true", help="Ensure host env is OK ")
    group1.add_argument(
        "-D", "--docker", action="store_true", help="Install/Update docker on host")

    group5 = doParser.add_argument_group("Remove docker things")
    group5.add_argument("-C", "--rm-all-containers", action="store_true")
    group5.add_argument("-I", "--rm-all-images", action="store_true")
    group5.add_argument("-V", "--rm-all-volumes", action="store_true")

    group6 = doParser.add_argument_group("Enviroment management parameters")
    # group6.add_argument("-d", "--regenerate-db", action="store_true")
    # group6.add_argument("-i", "--init-dev-env", action="store_true")
    group6.add_argument("-b", "--build-protobuf", action="store_true")
