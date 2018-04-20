from __future__ import absolute_import, division, print_function

import os
import sys
import traceback
from os.path import exists as fexists
from os.path import join as pjoin

# from fabric import operations
from fabric.api import cd, run
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

from aer import utils
from aer.commands.component.util import *
from states_db import odb
from utils import EasyDict

# from aer.states_db import odb

# pylint: disable=I0011,E1129


def entrypoint():

    # TODO handle in the .. cont sub-command
    if odb.arg.has.containers and odb.arg.containers:
        odb.run.containers = []
        for _C in odb.arg.containers:
            if _C in odb.cache.all_containers:
                odb.run.containers.append(_C)

    if docker_not_installed():
        install_docker()

    if odb.arg.deploy:
        deploy_all()


def deploy_all():
    temp_dir = "temp"
    run("mkdir -p " + temp_dir)
    allconfs = EasyDict()
    allconfs.update(odb.pth)
    allconfs.update(odb.run)
    allconfs.update(odb.cache)
    allconfs.var = odb.var
    with cd(temp_dir):
        # for cont_name_ in odb.arg.all_conts:
        #     cont_path = pjoin(odb.pth.docker_containers_root, cont_name_)
        #     call_container("populate_conf", cont_path, odb.acf)
        # generate_meta()
        for cont_name_ in odb.arg.containers:
            if cont_name_ in odb.cache.all_containers.keys():
                run_container(cont_name_, allconfs)


def run_container(cont_name, the_config):
    cont_path = odb.cache.all_containers[cont_name]

    run("mkdir -p " + cont_name)
    with cd(cont_name):
        run("rm -rf ./*")
        call_container("run_container", cont_path, the_config)
    return True


def call_container(function, cont_path, *args, **kwargs):
    """
            TODO make it possible to specify a different source .py

            Loads a remote file.py as a module and runs the specified function
            warns on no function or no file exists
            delets all traces of the module after function is ran

    """
    spathBK = sys.path[0]

    if not os.path.exists(cont_path + "/container_main.py"):
        print(magenta("Missing " + cont_path + "/container_main.py", bold=False))
        return False
    try:
        sys.path[0] = cont_path
        import container_main
        print(cyan("Executing " + function + " from " +
                   cont_path + "/container_main.py"))
        result = getattr(container_main, function)(*args, **kwargs)
        print(green("Succesfully ran " + function +
                    " from " + cont_path + "/container_main.py"))
    except Exception as ex:
        print(magenta("Exception in function " + function +
                      " in " + cont_path + "/container_main.py"))
        traceback.print_exc()
        return False
    finally:
        sys.path[0] = spathBK
        delete_module("container_main")
    return True


def delete_module(modname, paranoid=None):
    """
            fom https://mail.python.org/pipermail/tutor/2006-August/048596.html
            Deletes every reference to a specified module

            Used to remove evidence of functions from remotly called scripts
    """
    from sys import modules
    try:
        thismod = modules[modname]
    except KeyError:
        raise ValueError(modname)
    these_symbols = dir(thismod)
    if paranoid:
        try:
            paranoid[:]  # sequence support
        except:
            raise ValueError('must supply a finite list for paranoid')
        else:
            these_symbols = paranoid[:]
    del modules[modname]
    for mod in modules.values():
        try:
            delattr(mod, modname)
        except AttributeError:
            pass
        if paranoid:
            for symbol in these_symbols:
                if symbol[:2] == '__':  # ignore special symbols
                    continue
                try:
                    delattr(mod, symbol)
                except AttributeError:
                    pass
