from __future__ import absolute_import, division, print_function

import argparse
import os
import sys
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import env, lcd, local, quiet
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

import file_db_handler
from aer import commands, utils
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# from aer.states_db import odb

# pylint: disable=I0011,E1129,C0103

ARGUMENTS = None
ENTRYPOINT = None


def init_command_line():
    global ARGUMENTS
    global ENTRYPOINT

    main_parser = argparse.ArgumentParser(
        description='Command line utility for project development.', conflict_handler='resolve')
    main_parser.add_argument("-l", "--list", dest="list",
                             action="store_true", help='List everything')

    child_parser = main_parser.add_subparsers(
        title='subcommands', description='valid subcommands',
        help="Sub-Commands for deploying on different platforms")

    commands.init_subcommands(child_parser)

    ARGUMENTS = main_parser.parse_args()

    update_cmd_args(ARGUMENTS)
    commands.prepare_args(ARGUMENTS)

    # TODO quick read the values from odb.cache if entrypoint not CONT
    gen_conts_list()
    if odb.arg.has.list and odb.arg.list:
        list_all_info()

    try:
        ENTRYPOINT = ARGUMENTS.entrypoint
        del ARGUMENTS.entrypoint
    except :
        pass


def update_cmd_args(args):
    for arg_ in vars(args):
        if arg_ == "entrypoint":
            continue
        odb.arg[arg_] = getattr(args, arg_)


def start_entrypoint():
    print(cyan("Arguments :"))
    print(cyan(ARGUMENTS))
    print()

    if ENTRYPOINT is not None:
        ENTRYPOINT()
    else:
        print(magenta("No 'entrypoint' function set in set_defaults"))
        # print(magenta(ARGUMENTS))
        # raise Exception("No 'entrypoint' function specified for sub-command !")


def gen_conts_list():
    if "all_containers" not in odb.cache:
        odb.cache.all_containers = EasyDict()
    for croot_ in odb.pth.docker_containers_root:
        if fexists(croot_):
            for pth_ in os.listdir(croot_):
                cont_path = pjoin(croot_, pth_)
                if not os.path.isdir(cont_path):
                    continue
                if not os.path.isfile(pjoin(cont_path, "container_main.py")):
                    continue
                odb.cache.all_containers[pth_] = cont_path


def list_all_info():
    # print(cyan("Available hosts configurations:"))
    # for key_, val_ in odb.hst.items():
    #     print(key_)
    #     if "aliases" in val_ and isinstance(val_.aliases, list):
    #         print(blue("  " + ", ".join(val_.aliases)))

    print(cyan("Available containers:"))
    for cont_ in sorted(odb.cache.all_containers.keys()):
        print("\t",cont_)
