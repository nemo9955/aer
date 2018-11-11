# pylint: disable=I0011,E1129,E0611
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
        # print("----",db_path)
        with open(db_path) as datafile_db:
            data = json.load(datafile_db, object_hook=EasyDict)
            transfer_missing_elements(odb, data)
            # print("..............",json.dumps(odb.EXTRA_BUILD_FLAGS, indent=2))


def transfer_missing_elements(target_dict, source_dict, transfer_type=None):
    """Transferes missing elements from source to target recusevly
    """

    if transfer_type is None:
        transfer_type = source_dict.get("_transfer_type_", "recursive")

    for key_, val_ in source_dict.items():
        # print(key_,isinstance(val_, dict), val_)
        if isinstance(val_, dict):
            if key_ not in target_dict:
                target_dict[key_] = EasyDict()
            if transfer_type is None:
                transfer_type = val_.get("_transfer_type_", "recursive")
            # print("***********   ",transfer_type)

            if transfer_type == "recursive":
                transfer_missing_elements(target_dict[key_], val_, transfer_type)
            elif transfer_type == "update":
                target_dict[key_].update(val_)
            elif transfer_type == "overwrite":
                target_dict[key_] = copy.deepcopy(source_dict[key_])
                # target_dict[key_] = val_

        elif key_ not in target_dict:
            target_dict[key_] = copy.deepcopy(source_dict[key_])
            # target_dict[key_] = val_
        # else :
        #     target_dict[key_] = val_
            # target_dict[key_] = copy.deepcopy(source_dict[key_])


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


# def key_matches(key_, dic1_, dic2_):
# return  key_ in dic1_ and dic1_[key_] is not None and key_ in dic2_ and
# dic2_[key_] is not None and dic2_[key_] == dic1_[key_]


def write_to_db(file_path, file_dict):
    with open(file_path, 'w') as write_file:
        json.dump(file_dict, write_file, indent=2)

def run_tests():
    print("TESTING ___________ ")

    print("TESTING transfer_missing_elements ")
    d1=EasyDict()
    d1.a=1
    d1.b=1
    d1.c=1
    d1.d=EasyDict()
    d1.d.a=1
    d1.d.b=1

    d1._transfer_type_="update"
    d2=EasyDict()
    d2.a=20
    d2.c=20
    d2.d=EasyDict()
    d2.d.a=20
    d2.d.x=20
    transfer_missing_elements(d2,d1)
    expected = EasyDict({"a": 20, "d": {"a": 1, "x": 20, "b": 1}, "c": 20, "_transfer_type_": "update", "b": 1})
    # print(json.dumps(d2,indent=2))
    # print(json.dumps(d2))
    if d2 != expected :
        print(expected, "!=", json.dumps(d2) )
        raise Exception("transfer_missing_elements is different")


    d1._transfer_type_="recursive"
    d2=EasyDict()
    d2.a=20
    d2.c=20
    d2.d=EasyDict()
    d2.d.a=20
    d2.d.x=20
    transfer_missing_elements(d2,d1)
    expected = EasyDict({"a": 20, "d": {"a": 20, "x": 20, "b": 1}, "b": 1, "c": 20, "_transfer_type_": "recursive"})
    # print(json.dumps(d2,indent=2))
    # print(json.dumps(d2))
    if d2 != expected :
        print(expected, "!=", json.dumps(d2) )
        raise Exception("transfer_missing_elements is different")

    d1._transfer_type_="overwrite"
    d2=EasyDict()
    d2.a=20
    d2.c=20
    d2.d=EasyDict()
    d2.d.a=20
    d2.d.x=20
    transfer_missing_elements(d2,d1)
    expected = EasyDict({"a": 20, "d": {"a": 1, "b": 1}, "c": 20, "b": 1, "_transfer_type_": "overwrite"})
    # print(json.dumps(d2,indent=2))
    # print(json.dumps(d2))
    if d2 != expected :
        print(expected, "!=", json.dumps(d2) )
        raise Exception("transfer_missing_elements is different")






if __name__ == "__main__":
    run_tests()