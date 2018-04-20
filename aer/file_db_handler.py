from __future__ import absolute_import, division, print_function

import copy
import json
import os
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import (env, execute, fastprint, hide, lcd, local, prompt,
                        quiet, run, sudo, task)
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib.console import confirm

# from aer.states_db import odb
# from aer.utils import EasyDict
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# pylint: disable=I0011,E1129


def handle():
    from aer import arguments as args

    # TODO try to obtain file_db path from ENV
    if not fexists(odb.pth.user_db):
        generate_user_db()

    # TODO detach file_db and arguments completly
    args.init_command_line()

    update_fabric_env()

    for dbp_ in odb.pth.file_dbs:
        load_file_db(dbp_)

    args.start_entrypoint()

    write_to_db(odb.pth.cache_db, {"cache": odb.cache})



def update_fabric_env():
    for key_, val_ in odb.env.items():
        env[key_] = val_


def generate_user_db():
    user_db_path = odb.pth.user_db
    user_dict = EasyDict()
    # user_dict.pth = odb.pth.copy()
    user_dict.var = odb.var.copy()
    write_to_db(user_db_path, user_dict)


def load_file_db(db_path):
    if fexists(db_path):
        with open(db_path) as datafile_db:
            data = json.load(datafile_db,object_hook=EasyDict)
            transfer_missing_elements(odb, data)


def transfer_missing_elements(target_dict, source_dict):
    """Transferes missing elements from source to target recusevly
    """

    for key_,val_ in source_dict.items():
        if isinstance(val_, dict):
            if key_ not in target_dict:
                target_dict[key_] = EasyDict()
            transfer_type = val_.get("_transfer_type_", "recursive")

            if transfer_type == "recursive":
                transfer_missing_elements(target_dict[key_], val_)
            elif transfer_type == "update":
                target_dict[key_].update(val_)
            elif transfer_type == "overwrite":
                target_dict[key_]=val_

        # if isinstance(source_dict[key_],list) and  isinstance(source_dict[key_][0],dict):
        #     if key_ not in target_dict:
        #         target_dict[key_] = []
        #     for src_ in source_dict[key_]:
        #         if not isinstance(src_,dict):
        #             continue
        #         match = False
        #         for tar_ in target_dict[key_]:
        #             # TODO make a list of bool with ID keys loaded from odb and check if any(matches):
        #             if key_matches("pth_full", src_, tar_) or key_matches("pth_alias", src_, tar_) :
        #                 match = True
        #         if not match:
        #             temp = EasyDict()
        #             target_dict[key_].append(temp)
        #             transfer_missing_elements(temp, src_)

        elif key_ not in target_dict:
            target_dict[key_] = copy.deepcopy(source_dict[key_])

# def key_matches(key_, dic1_, dic2_):
# return  key_ in dic1_ and dic1_[key_] is not None and key_ in dic2_ and
# dic2_[key_] is not None and dic2_[key_] == dic1_[key_]


def write_to_db(file_path, file_dict):
    with open(file_path, 'w') as write_file:
        json.dump(file_dict, write_file, indent=2)
