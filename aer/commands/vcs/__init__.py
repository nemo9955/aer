from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.vcs.vcs import entrypoint

# pylint: disable=I0011,E1129


def init(parent_parser):
    vcsParser = parent_parser.add_parser(
        'vcs', help='Version control systems for easy interaction with needed repositories, be them yours or third party\'s  ', conflict_handler='resolve')  # add_help=False,
    vcsParser.set_defaults(entrypoint=entrypoint)

    group1 = vcsParser.add_argument_group("Misc")
    groupTags = vcsParser.add_argument_group("Tags related arguments")
    groupMajor = vcsParser.add_argument_group("Major vcs actions")

    group1.add_argument("-L", "--list-local-libs", dest="list_local_libs", action="store_true")
    group1.add_argument("-LL", "--list-all-libs", dest="list_all_libs", action="store_true")
    group1.add_argument("-m", "--list-details", dest="list_details", action="store_true")
    group1.add_argument("-M", "--list-more-details", dest="list_more_details", action="store_true")

    groupTags.add_argument('-t','--tags-all', dest="tags_all", nargs='*', help='Only libs with these tags will be managed', default="")
    groupTags.add_argument('-T','--tags-one', dest="tags_one", nargs='*', help='Only libs with at least one of the folowing tags will be managed', default="")

    groupMajor.add_argument("-e", "--libs-ensure", dest="libs_ensure",help="Ensure (if config and conditions allow) that the libs are available locally", action="store_true")
    groupMajor.add_argument("-u", "--libs-update", dest="libs_update", action="store_true", help="Also ensures libs are updated!")
    groupMajor.add_argument("-p", "--libs-push", dest="libs_push", action="store_true")
