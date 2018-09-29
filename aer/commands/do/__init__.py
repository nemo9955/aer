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
    # target_group.add_argument('-a', "--alias-config", dest="alias_config",
    #                           help='Select config from alias')
    target_group.add_argument('-t', "--target-host", dest="target_host",
                              help='Specify exact host to deploy the containers to.')

    group1 = doParser.add_argument_group("Host/container actions")
    # group1.add_argument(
    #     "-e", "--ensure-env", dest="ensure_env", action="store_true", help="Ensure host env is OK ")
    group1.add_argument(
        "-D", "--docker", dest="docker", action="store_true", help="Install/Update docker on host")

    group5 = doParser.add_argument_group("Remove docker things")
    group5.add_argument("-C", "--rm-all-containers", dest="rm_all_containers", action="store_true")
    group5.add_argument("-I", "--rm-all-images", dest="rm_all_images", action="store_true")
    group5.add_argument("-V", "--rm-all-volumes", dest="rm_all_volumes", action="store_true")

    group6 = doParser.add_argument_group("Enviroment management parameters")
    # group6.add_argument("-d", "--regenerate-db", dest="regenerate_db", action="store_true")
    # group6.add_argument("-i", "--init-dev-env", dest="init_dev_env", action="store_true")
    group6.add_argument("-b", "--build-protobuf", dest="build_protobuf", action="store_true")
