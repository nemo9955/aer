from __future__ import absolute_import, division, print_function

import argparse
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.colors import blue, cyan, green, magenta, red, white, yellow

# from aer.api import *
from aer.commands.node.node import espmake_entry, esptool_entry, nodes_entry
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# pylint: disable=I0011,E1129


def init(pparser):
    espmake_pars = pparser.add_parser('espmake', help='Extension around the chosen Makefile for ESP___',
                                      conflict_handler='resolve', add_help=False, prefix_chars='\0')
    espmake_pars.set_defaults(entrypoint=espmake_entry)
    espmake_pars.add_argument('passing_args', nargs=argparse.REMAINDER)

    esptool_pars = pparser.add_parser('esptool', help='Extension around esptool.py',
                                      conflict_handler='resolve', add_help=False, prefix_chars='\0')
    esptool_pars.set_defaults(entrypoint=esptool_entry)
    esptool_pars.add_argument('passing_args', nargs=argparse.REMAINDER)

    nodes_pars = pparser.add_parser(
        'node', help='Utility to manage dev boards like ARDUINO/ESP8266/ESP32/Wemos_XI')
    search_qu = nodes_pars.add_argument_group("Search queryes")
    moptions_gr = nodes_pars.add_argument_group("Make options")
    make_action = nodes_pars.add_argument_group("Make actions")
    board_detect = nodes_pars.add_argument_group("Boards detection")

    nodes_pars.set_defaults(entrypoint=nodes_entry)
    moptions_gr.add_argument('-me', "--make-e",
                             help='Add -e argument to make', action="store_true")
    moptions_gr.add_argument('-md', "--make-d",
                             help='Add -d argument to make', action="store_true")
    nodes_pars.add_argument("-n", '--show-serial',
                            help='Terminal will show board serial', action="store_true")
    nodes_pars.add_argument("-N", "--serial-baud", metavar="baud",
                            help='Select serial terminal baud rate', default=odb.var.serial_baud)
    moptions_gr.add_argument("-c", "--clear-builds",
                             help='Clear the builds binaries', action="store_true")

    make_action.add_argument("-e", "--erase-flash",
                             help='Erase flash of the ESP', action="store_true")
    make_action.add_argument("-d", "--flash-filesystem",
                             help='Flash root directory system', action="store_true")
    make_action.add_argument("-o", "--http-ota-update",
                             help='Update ESP OTA using /update curl command', action="store_true")
    make_action.add_argument('-f', "--flash",
                             help='Flash the node', action="store_true")

    search_qu.add_argument('-i', "--in-chip-id", metavar="id",
                           help='Chip ID in HEX representation MUST contain', default="")
    search_qu.add_argument('-s', "--in-sketch", metavar="search",
                           help='String the name of the sketch must contain', default="")
    search_qu.add_argument('-D', "--in-filesystem", metavar="search",
                           help='String the name of the filesystem root folder must contain', default="")

    board_detect.add_argument('-P', "--boards-from-ports",
                              help='Iterate thru all the valid ports to find vallid boards', action="store_true")
    board_detect.add_argument('-M', "--boards-from-mdns",
                              help='Iterate thru all the connected boards', action="store_true")
