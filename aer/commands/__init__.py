from __future__ import division, print_function

from aer.commands import backup, component, do, imgos, node, vcs
from fabric.api import env
from states_db import odb

# pylint: disable=I0011,E1129


def init_subcommands(child_parser):
    node.init(child_parser)
    component.init(child_parser)
    imgos.init(child_parser)
    do.init(child_parser)
    backup.init(child_parser)
    vcs.init(child_parser)


def prepare_args(args):
    # print(vars(args))
    # import json
    # print(json.dumps(odb.arg,indent=2))
    if odb.arg.has.target_host:
        env.host_string = odb.arg.target_host
