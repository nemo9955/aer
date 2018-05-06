# pylint: disable=I0011,E1129,E0611
from __future__ import absolute_import, division, print_function

import datetime
import json
import os
import re
import uuid
from os.path import exists as fexists
from os.path import join as pjoin

# from fabric.api import *
from fabric.api import env, lcd, local, prompt, quiet
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

# from aer.api import *
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# from aer.states_db import odb



def entrypoint():
    if odb.arg.libs_ensure:
        ensure_libs()

    if odb.arg.libs_push:
        push_libs()

    if odb.arg.list_all_libs:
        list_all_libs()

    if odb.arg.list_local_libs:
        list_all_libs(just_local=True)

    # print(json.dumps(odb.pth, indent=3))
    # print(json.dumps(odb,indent=3))


def list_all_libs(just_local=False):
    for libd in libs_iterator():
        if just_local and not lib_exists(libd):
            continue
        print(cyan(libd.full_path))
        if odb.arg.list_more_details:
            print(json.dumps(libd, indent=4))


def push_libs():
    for libd in libs_iterator():
        if not libd.can_push:
            continue
        if libd.obtain_type != "git_clone":
            continue
        if not lib_exists(libd):
            continue

        with lcd(libd.full_path):
            local("pwd")
            local("git add --all")
            stat_str = local("git status", capture=True)
            if "nothing to commit" in stat_str:
                continue
            local("git status")
            comm_message = prompt(
                "Add commit message, blank to skip this repo:")
            if comm_message.strip() == "":
                continue
            local("git commit -m \'%s\' " % comm_message)
            local(libd.push_command)


def update_project(libd):
    if not odb.arg.libs_update:
        return False

    if libd.slow and not odb.arg.including_slow:
        print(
            yellow(libd.format("Skipping {folder} because update slow are disabled")))
        return False

    if not lib_exists(libd):
        print(red(libd.format("Project not found locally : {folder} ")))
        return False

    print(cyan(str(libd.root_path)) + "/" + green(str(libd.folder)), libd.url)
    with lcd(libd.full_path):
        # status = local(libd.update_command.format(**libd)).succeeded
        status = local(libd.format("{update_command}")).succeeded
    return status


def libs_iterator():
    for lib_ in odb.libs_manager.values():
        if not isinstance(lib_, dict):
            continue
        for grepo_ in lib_.get("git_repo", []):
            libd = EasyDict()
            libd.update(odb.dft.lib_proj)
            libd.update(grepo_)

            libd.root_path = lib_get_parent_path(lib_)
            libd.can_push = lib_.get("can_push")
            libd.full_path = pjoin(libd.root_path, libd.folder)

            yield libd


def ensure_libs():
    """
    Clones/Gets all libs to the dev machine
    """

    for libd in libs_iterator():
        # print( green("Getting libs for folder " + json.dumps(libd,indent=2)))
        with quiet():
            local("mkdir -p {} ".format(libd.root_path))

        if not (libd.has.url and libd.has.folder):
            print(red("Lib must have url and folder specified " + str(libd)))
            continue

        if libd.slow and not odb.arg.including_slow:
            print(
                yellow(libd.format("Skipping {folder} because 'slow=True' are excluded")))
            continue

        fresh_get = False

        if lib_exists(libd):
            update_project(libd)

        if lib_exists(libd):
            pass
        elif libd.obtain_type == "git_clone":
            fresh_get = get_using_command(libd)
        elif libd.obtain_type == "github_latest":
            fresh_get = get_using_latest(libd)
        elif libd.obtain_type == "wget_direct":
            fresh_get = get_using_wget(libd)

        if fresh_get:
            finished_ok = run_after_command(libd)
            if finished_ok:
                print(
                    green("Project available locally : {folder}".format(**libd)))


def get_using_command(libd):
    # with lcd(libd.root_path):
    return local(libd.format("cd {root_path} && {get_command}")).succeeded


def get_using_wget(libd):
    if not libd.has.download_url:
        print(red("Must have download_url " + str(libd)))

    return local(libd.format("cd {root_path} && wget {download_url}")).succeeded


def get_using_latest(libd):
    if not (libd.has.download_url and libd.has.validate_latest):
        print(red("Must have download_url and validate_latest " + str(libd)))
        return False
    body_string = None

    with quiet():
        latest_getc = libd.format("curl {download_url}/releases/latest")
        latest_body = local(latest_getc, capture=True)

    if "redirected" in latest_body:
        the_url = None
        for i in latest_body.split("\""):
            if libd.format("{download_url}") in i:
                the_url = i
                break

        if the_url is None:
            print(latest_getc)
            print(latest_body)
            return False

        with quiet():
            body_string = local("curl " + the_url, capture=True)
    else:
        body_string = latest_body

    if body_string is None:
        return False

    dld_body = body_string.split("\"")

    dld_url = None
    for some_str_ in dld_body:
        valid_url = re.compile(libd.validate_latest)
        if valid_url.match(some_str_):
            dld_url = some_str_
            break

    if dld_url is None:
        for some_str_ in dld_body:
            if "http" in some_str_:
                print(some_str_)
        return False

    dld_url = "https://github.com" + dld_url
    print(cyan("Downloading latest github release : " + dld_url))
    res = local(libd.format(
        "cd {root_path} && wget {0}", dld_url), capture=True)
    # res = local("cd {root_path} && wget {dld_url} ".format(
    #     dld_url=dld_url, **libd), capture=True)
    return res.succeeded


def run_after_command(libd):
    if not libd.has.after_command:
        return True
    print(
        cyan('Executing after_command "{after_command}" for {folder}'.format(**libd)))
    with quiet() and lcd(libd.root_path):
        return local(libd.after_command.format(**libd)).succeeded


def lib_exists(libd):
    """
    Returns True/False if the library/project/repository is present on the local dev machine
    """
    return fexists(libd.full_path)


# def link_dependencies():
#     esp8266_libs = pjoin(odb.pth.trd_deploy_libs, "esp8266/")
#     print()
#     # print( odb.pth.node_dir)
#     print(odb.pth.trd_sketch_libs)


def lib_get_parent_path(lib_):
    parent_dir = None
    if lib_.has.pth_full:
        parent_dir = lib_["pth_full"]
    if lib_.has.pth_alias:
        parent_dir = odb.pth[str(lib_.pth_alias)]
    return parent_dir
