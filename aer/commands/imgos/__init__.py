from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.imgos.imgos import entrypoint

# pylint: disable=I0011,E1129


def init(parent_parser):
    from aer.commands import imgos

    cont_parser = parent_parser.add_parser(
        'imgos', help='Command for writing and preparing OS images', conflict_handler='resolve')

    cont_parser.set_defaults(entrypoint=entrypoint)
    # contParser.add_argument('args', nargs=argparse.REMAINDER)
    burn_group = cont_parser.add_argument_group("Burn options",
                                                "Args for burning an image to a SD card")
    burn_group.add_argument('--ofl', metavar="of",
                            help='Path to SD card', default=None)
    burn_group.add_argument('--ifl', metavar="if",
                            help='Path of image to be burned', default=None)
    burn_group.add_argument("-b", '--burn',
                            action="store_true", help='Burn an image to card')
    burn_group.add_argument('--bs', help='Block size', default="4M")

    write_group = cont_parser.add_argument_group("Write options",
                                                 "Used to write data to the card after burn")
    write_group.add_argument("-w", '--write',
                             action="store_true", help='Write changes to card')
    write_group.add_argument("-s", '--add_ssh',
                             action="store_true", help='Add shh file to enable SHH access')
