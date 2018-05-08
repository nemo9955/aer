# pylint: disable=I0011,E1129,E0401,E0602,E0611
from __future__ import absolute_import, division, print_function

import copy
import os
import re
import sys
import time
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import env, lcd, local, prompt, quiet
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

from aer import utils
# from aer.api import *
from aer.file_db_handler import transfer_missing_elements, write_to_db
from aer.commands.vcs import vcs
# from aer.states_db import odb
from aer.utils import pick_from_list
from states_db import odb
from utils import EasyDict, RecursiveFormatter


def nodes_entry():
    if odb.arg.clear_builds:
        local("rm -rf /tmp/mkESP")

    boards_list = scan_for_boards()

    for bcnf in boards_list.values():
        # print_board_meta(bcnf)
        status_ok = True
        if bcnf.has.CHIP_ID:

            print(yellow("Active board chip id : " + bcnf.CHIP_ID))

        save_board_parameters(bcnf)
        if odb.arg.erase_flash:
            bcnf["action"] = "erase_flash"
            bcnf.DEMO = 1
            status_ok = call_makefile(bcnf)

        save_board_parameters(bcnf)
        if odb.arg.http_ota_update:
            bcnf.SKETCH = obtain_sketch(bcnf)
            bcnf["action"] = "http"
            status_ok = call_makefile(bcnf)

        save_board_parameters(bcnf)
        if odb.arg.flash and bcnf.has.PORT:
            bcnf.SKETCH = obtain_sketch(bcnf)
            bcnf["action"] = "flash"
            status_ok = call_makefile(bcnf)

        save_board_parameters(bcnf)
        if odb.arg.flash_filesystem:
            bcnf.FILESYSTEM = obtain_filesystem(bcnf)
            bcnf.DEMO = 1
            bcnf["action"] = "flash_fs"
            status_ok = call_makefile(bcnf)

        save_board_parameters(bcnf)
        if odb.arg.show_serial and status_ok and bcnf.has.PORT:
            local("miniterm.py --develop --exit-char 3 " +
                  str(bcnf.PORT) + " " + str(odb.arg.serial_baud))


def chip_id_has_port(chip_id):
    bcnf = get_board_conf(chip_id)
    if bcnf.has.PORT and bcnf.PORT in get_ports_list():
        real_cid = get_chip_id(bcnf.PORT)
        if real_cid == chip_id:
            print(cyan("Found matching cached port for CHIP ID " + chip_id))
            return True
    print(magenta("Cached port miss-match for board {} ".format(chip_id)))
    print(yellow("Run 'aer node -P' to refresh cache "))
    scan_serials()
    sys.exit(42)


def scan_serials():
    for ser_ in get_ports_list():
        bcnf = port_to_board(ser_)
        bcnf.PORT = ser_
        save_board_parameters(bcnf)


def port_to_board(board_port):
    chip_id = get_chip_id(board_port)

    bcnf = get_board_conf(chip_id)
    bcnf.PORT = board_port
    bcnf.CHIP_ID = chip_id
    bcnf.CHIP_ID_SHORT = chip_id[-4:]
    if not bcnf.has.MAC:
        bcnf.MAC = get_att_chip_mac(bcnf.PORT)
    save_board_parameters(bcnf)
    return bcnf


def scan_for_boards():
    boards_list = EasyDict()

    if odb.arg.in_chip_id != "":
        valid_cids = [cids_ for cids_ in odb.boards_db.keys()
                      if odb.arg.in_chip_id in cids_]
        chip_id = pick_from_list(valid_cids)
        if odb.boards_db.has[chip_id] and chip_id_has_port(chip_id):
            bcnf = get_board_conf(chip_id)
            boards_list[bcnf.CHIP_ID] = bcnf
            return boards_list
        # else:
        #     print( magenta("No saved CHIP ID that containes {} : {}".format(odb.arg.in_chip_id, str(odb.boards_db.keys()))))
        #     print( yellow("Run 'aer node -P' to detect boards "))
        #     sys.exit(42)

    if odb.arg.boards_from_ports:
        for board_port in get_ports_list():
            bcnf = port_to_board(board_port)
            if boards_list.has[bcnf.CHIP_ID]:
                transfer_missing_elements(boards_list[bcnf.CHIP_ID], bcnf)
            else:
                boards_list[bcnf.CHIP_ID] = bcnf

    if odb.arg.boards_from_mdns:
        for bcnf_ in odb.boards_db.values():
            if bcnf_.has.CHIP_ID and odb.arg.in_chip_id in bcnf_.CHIP_ID:
                bcnf = get_board_conf(bcnf_.CHIP_ID)
                if mdns_exists(bcnf, 1):
                    if boards_list.has[bcnf.CHIP_ID]:
                        transfer_missing_elements(
                            boards_list[bcnf.CHIP_ID], bcnf)
                    else:
                        boards_list[bcnf.CHIP_ID] = bcnf

    for key_, val_ in boards_list.items():
        if val_.has.CHIP_ID and odb.arg.in_chip_id not in val_.CHIP_ID:
            boards_list.pop(key_, None)

    return boards_list


def mdns_exists(bcnf, timeout=0.5, tries=1):
    look_addr = ["HTTP_ADDR", "WIFI_STATION_IP", "VALID_BOARD_ADDRESS"]
    look_addr.extend(look_addr)
    look_addr.extend(look_addr)
    for addr_ in look_addr:
        if bcnf.has[addr_]:
            address = "{" + addr_ + "}"
            pout = local(bcnf.format(
                "timeout {0} ping {1} -c {2} || true", timeout, tries, address), capture=True)
            presult = re.search(
                bcnf.format('PING {0} \(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\)', address), pout)
            if presult:
                bcnf.VALID_BOARD_ADDRESS = presult.group(1)
                print(
                    yellow(bcnf.format("Found {address} at {VALID_BOARD_ADDRESS} ", address)))
                return True
    return False


def save_board_parameters(bcnf):
    basic_params = ["FILESYSTEM",
                    "SKETCH",
                    "CHIP_ID",
                    "PORT",
                    "MAC",
                    "CHIP_ID_SHORT",
                    "WIFI_STATION_IP",
                    "VALID_BOARD_ADDRESS",
                    "HTTP_URI", "HTTP_PWD", "HTTP_USR", "HTTP_ADDR"]

    changed = False
    transfer_missing_elements(odb.EXTRA_BUILD_FLAGS, odb.dft.EXTRA_BUILD_FLAGS)
    transfer_missing_elements(odb.BOARD_SPECIFIC_VARS,
                              odb.dft.BOARD_SPECIFIC_VARS)

    for bpar_ in basic_params:
        if bcnf.has[bpar_]:
            odb.boards_db[bcnf.CHIP_ID][bpar_] = bcnf[bpar_]
            changed = True

    if changed:
        towrite = EasyDict()
        towrite.boards_db = odb.boards_db
        towrite.EXTRA_BUILD_FLAGS = odb.EXTRA_BUILD_FLAGS
        towrite.BOARD_SPECIFIC_VARS = odb.BOARD_SPECIFIC_VARS
        write_to_db(odb.pth.boards_db, towrite)


def get_board_conf(chip_id):
    """Loads/generates a configuration in odb.boards_db
    The user then can edit the generated conf to suite the board and on the next run, the specified chached conf will be used for that board ID
    """
    if chip_id not in odb.boards_db:
        print(yellow(
            "Creating default board config for {}; consider updating the cached config".format(chip_id)))

        print(green("What type of chip is {} ?".format(chip_id)))

        board_defaults = pick_from_list(odb.dft.boards_db.keys())
        odb.boards_db[chip_id] = EasyDict(odb.dft.boards_db[board_defaults])

        print(green("What type of board is {} ?".format(chip_id)))
        board_type = pick_from_list(odb.dft.boards_types[board_defaults])
        odb.boards_db[chip_id].BOARD = board_type

        if board_type == "d1_mini_lite":
            odb.boards_db[chip_id].UPLOAD_SPEED = 460800

        board_descript = prompt("Short description for this board: ")
        if board_descript != "":
            odb.boards_db[chip_id].DESCRIPTION = board_descript

    bcnf = EasyDict()
    transfer_missing_elements(bcnf, odb.boards_db[chip_id])
    transfer_missing_elements(bcnf, odb.dft.boards_db[bcnf.VARIANT])
    # bcnf.EXTRA_BUILD_FLAGS.update( odb.dft.EXTRA_BUILD_FLAGS)
    transfer_missing_elements(bcnf.EXTRA_BUILD_FLAGS, odb.EXTRA_BUILD_FLAGS)
    transfer_missing_elements(
        bcnf.BOARD_SPECIFIC_VARS, odb.BOARD_SPECIFIC_VARS)
    return bcnf


def call_makefile(bcnf):
    return plerup_make(bcnf)
    # return thunderace_make(bcnf)


def plerup_make(bcnf):
    bcnf.makefile_path = os.path.join(
        odb.pth.trd_deploy_libs, "makeEspArduino/makeEspArduino.mk")

    if bcnf.has.VARIANT:
        bcnf.ESP_ROOT = pjoin(odb.pth.trd_deploy_libs, bcnf.VARIANT)

    bcnf.ESPTOOL_PY = pjoin(odb.pth.trd_deploy_libs, "esptool", "esptool.py")

    bcnf.SOME_DEPS = " ".join(odb.pth.include_libs)

    bcnf.espmake = 'make  '
    # bcnf.espmake += 'CXXFLAGS=\'std=c++17\' '
    # bcnf.espmake += 'LDFLAGS=-T/home/me/esp-open-sdk/sdk/ld/eagle.app.v6.ld '
    if odb.arg.get("make_e", False):
        bcnf.espmake += '-e '
    if odb.arg.get("make_d", False):
        bcnf.espmake += '-d '

    # TODO exit if no makefile path
    bcnf.espmake += '-f {makefile_path} '

    if bcnf.has.BOARD:
        bcnf.espmake += 'BOARD="{BOARD}" '

    if bcnf.has.FLASH_DEF:
        bcnf.espmake += 'FLASH_DEF="{FLASH_DEF}" '

    if bcnf.has.PORT:
        bcnf.espmake += 'UPLOAD_PORT="{PORT}" '

    if bcnf.has.SKETCH:
        bcnf.espmake += 'SKETCH="{SKETCH}" '

    if bcnf.has.FILESYSTEM:
        bcnf.espmake += 'FS_DIR="{FILESYSTEM}" '

    if bcnf.has.ESP_ROOT:
        bcnf.espmake += 'ESP_ROOT="{ESP_ROOT}" '

    if bcnf.has.CHIP:
        bcnf.espmake += 'CHIP="{CHIP}" '

    if bcnf.has.UPLOAD_SPEED:
        bcnf.espmake += 'UPLOAD_SPEED="{UPLOAD_SPEED}" '

    if bcnf.has.SOME_DEPS:
        bcnf.espmake += 'CUSTOM_LIBS=" {SOME_DEPS} " '

    if bcnf.has.EXTRA_BUILD_FLAGS:
        extra_str = ""
        for def_, val_ in bcnf.EXTRA_BUILD_FLAGS.items():
            # If define starts with _S_ it will be surounded by ""
            if def_.startswith("_S_"):
                extra_str += ' -D{0}="{1}" '.format(def_, val_)
            else:
                extra_str += ' -D{0}={1} '.format(def_, val_)
        for char_ in "()\";":
            extra_str = extra_str.replace(char_, "\\" + char_)
        bcnf.espmake += 'BUILD_EXTRA_FLAGS=\'{}\' '.format(extra_str)

    if bcnf.has.ESPTOOL_PY:
        bcnf.espmake += 'ESPTOOL="{ESPTOOL_PY}" '

    if bcnf.has.DEMO and not bcnf.has.SKETCH:
        bcnf.espmake += 'DEMO="{DEMO}" '

    if odb.arg.has.http_ota_update and odb.arg.http_ota_update and mdns_exists(bcnf, 1):
        bcnf.espmake += 'HTTP_ADDR="{VALID_BOARD_ADDRESS}" '
    elif bcnf.has.HTTP_ADDR:
        bcnf.espmake += 'HTTP_ADDR="{HTTP_ADDR}" '
    elif bcnf.has.VALID_BOARD_ADDRESS:
        bcnf.espmake += 'HTTP_ADDR="{VALID_BOARD_ADDRESS}" '

    if bcnf.has.HTTP_URI:
        bcnf.espmake += 'HTTP_URI="{HTTP_URI}" '

    if bcnf.has.HTTP_PWD:
        bcnf.espmake += 'HTTP_PWD="{HTTP_PWD}" '

    if bcnf.has.HTTP_USR:
        bcnf.espmake += 'HTTP_USR="{HTTP_USR}" '

    if bcnf.has.action:
        bcnf.espmake += ' {action} '

    print(cyan(bcnf.format("{espmake}").replace(
        "  ", " ").replace(" ", "\n")), "\n")

    res = local(bcnf.format("{espmake}"))
    return res.succeeded


def thunderace_make(bcnf):
    """
    Not worcking, hangs at the begining of the makefile !!!!
    """

    bcnf.makefile_path = os.path.join(
        odb.pth.trd_deploy_libs, "Esp8266-Arduino-Makefile/espXArduino.mk")

    bcnf.espmake = 'make '
    if bcnf.has.VARIANT:
        bcnf.espmake += 'ARDUINO_ARCH="{VARIANT}" '
        bcnf.ESP_ROOT = pjoin(odb.pth.trd_deploy_libs, bcnf.VARIANT)

    bcnf.ESPTOOL_PY = pjoin(odb.pth.trd_deploy_libs,
                            "esptool", "esptool.py")

    bcnf.SOME_DEPS = " ".join(odb.pth.include_libs)

    bcnf.espmake = 'make '
    if odb.arg.get("make_e", False):
        bcnf.espmake += '-e '
    if odb.arg.get("make_d", False):
        bcnf.espmake += '-d '

    # TODO exit if no makefile path
    bcnf.espmake += '-f {makefile_path} '
    bcnf.espmake += 'ESP8266_VERSION="" '
    bcnf.espmake += 'F_CPU="80000000L" '

    if bcnf.has.BOARD:
        bcnf.espmake += 'ARDUINO_VARIANT="{BOARD}" '
        bcnf.espmake += 'BUILD_OUT="/tmp/mkESP/{}" '.format(bcnf.BOARD)

    # if bcnf.has.FLASH_DEF:
    #     bcnf.espmake += 'FLASH_DEF="{FLASH_DEF}" '

    if bcnf.has.PORT:
        bcnf.espmake += 'SERIAL_PORT="{PORT}" '

    if bcnf.has.SKETCH:
        bcnf.espmake += 'SKETCH="{SKETCH}" '

    if bcnf.has.FILESYSTEM:
        bcnf.espmake += 'FS_DIR="{FILESYSTEM}" '

    if bcnf.has.ESP_ROOT:
        bcnf.espmake += 'ARDUINO_HOME="{ESP_ROOT}" '

    if bcnf.has.CHIP:
        bcnf.espmake += 'CHIP="{CHIP}" '

    if bcnf.has.UPLOAD_SPEED:
        bcnf.espmake += 'UPLOAD_SPEED="{UPLOAD_SPEED}" '

    if bcnf.has.EXTRA_BUILD_FLAGS:
        extra_str = ""
        for def_, val_ in bcnf.EXTRA_BUILD_FLAGS.items():
            # If define starts with _S_ it will be surounded by ""
            if def_.startswith("_S_"):
                extra_str += ' -D{0}="{1}" '.format(def_, val_)
            else:
                extra_str += ' -D{0}={1} '.format(def_, val_)
        for char_ in "()\";":
            extra_str = extra_str.replace(char_, "\\" + char_)
        bcnf.espmake += 'USER_DEFINE=\'{}\' '.format(extra_str)
        # bcnf.ESPTOOL = None

    # if bcnf.has.ESPTOOL_PY:
    #     bcnf.espmake += 'ESPTOOL="{ESPTOOL_PY}" '

    # if bcnf.has.DEMO and not bcnf.has.SKETCH:
    #     bcnf.espmake += 'DEMO="{DEMO}" '

    # if  odb.arg.http_ota_update and mdns_exists(bcnf, 1):
    #     bcnf.espmake += 'HTTP_ADDR="{VALID_BOARD_ADDRESS}" '
    # elif  bcnf.has.HTTP_ADDR :
    #     bcnf.espmake += 'HTTP_ADDR="{HTTP_ADDR}" '
    # elif bcnf.has.VALID_BOARD_ADDRESS :
    #     bcnf.espmake += 'HTTP_ADDR="{VALID_BOARD_ADDRESS}" '

    # if bcnf.has.HTTP_URI:
    #     bcnf.espmake += 'HTTP_URI="{HTTP_URI}" '

    # if bcnf.has.HTTP_PWD:
    #     bcnf.espmake += 'HTTP_PWD="{HTTP_PWD}" '

    # if bcnf.has.HTTP_USR:
    #     bcnf.espmake += 'HTTP_USR="{HTTP_USR}" '

    if bcnf.has.action and bcnf.action == "flash":
        bcnf.espmake += ' upload '

    print(cyan(bcnf.format("{espmake}").replace(
        "  ", " ").replace(" ", "\n")), "\n")

    res = local(bcnf.format("{espmake}"))
    return res.succeeded


def run_espmake(str_args):
    """
    TODO move some constants to the states_db module
    """
    bcnf = EasyDict()
    bcnf.ESP_ROOT = pjoin(odb.pth.trd_deploy_libs, "esp8266")
    bcnf.DEMO = 1
    bcnf.action = str_args
    return call_makefile(bcnf)


def obtain_filesystem(bcnf):
    if bcnf.has.FILESYSTEM and odb.arg.in_filesystem in bcnf.FILESYSTEM and os.path.isdir(bcnf.FILESYSTEM):
        return bcnf.FILESYSTEM

    fs_list = []
    for libd in vcs.libs(tags_one=["dep", "dependancy", "filesystem"]):
        # print(libd.full_path)
        fs_list.extend(utils.all_subdirs(libd.full_path))

    all_elements = ["data", "filesystems", "filesystem"]
    fs_list = utils.elements_endswith(fs_list, all_elements)

    req_elements = [odb.arg.in_filesystem]
    fs_list_query = utils.elements_contain(fs_list, req_elements)

    if len(fs_list_query) > 0:
        return pick_from_list(fs_list_query)

    return pick_from_list(fs_list)


def obtain_sketch(bcnf):
    if bcnf.has.SKETCH and odb.arg.in_sketch in bcnf.SKETCH and os.path.isfile(bcnf.SKETCH):
        return bcnf.SKETCH

    sk_list = []
    for libd in vcs.libs(tags_one=["dep", "dependancy"]):
        # print(libd.full_path)
        sk_list.extend(utils.all_subfiles(libd.full_path))

    all_elements = [".ino", ".c", ".cpp"]
    sk_list_src = utils.elements_endswith(sk_list, all_elements)

    query_elements = [odb.arg.in_sketch]
    sk_list_query = utils.elements_contain(sk_list_src, query_elements)

    if len(sk_list_query) > 0:
        return pick_from_list(sk_list_query)
    else:
        print(yellow("No Arduino/C/C++ specific fils found"))

    return pick_from_list(sk_list_src)


# def filter_sketch_list(sk_list, filter_elem):

    # meta_filter.append("META-DATA")
    # sk_list_meta = filter_sketch_list(sk_list_src, meta_filter)

    # if len(sk_list_meta) > 0:
    #     return sk_list_meta
    # else:
    #     print( yellow("Matching META-DATA not found for {} ".format(" ".join(meta_filter))))
#     valid_sks = []

#     for ske in sk_list:
#         with open(ske, 'r') as f:
#             sk_str = f.read()
#             if all(i in sk_str for i in filter_elem):
#                 valid_sks.append(ske)
#     return valid_sks


def espmake_entry():
    status = run_espmake(" ".join(odb.arg.passing_args))
    return status


def run_esptool(str_args, capt=False):
    return local(" python3 " + odb.pth.esptool_py + " " + str_args, capture=capt)
    # if capt:
    #     with quiet():
    #         return local(odb.pth.esptool_py + " " + str_args, capture=capt)
    # else:
    #     return local(odb.pth.esptool_py + " " + str_args, capture=capt)


def esptool_entry():
    status = run_esptool(" ".join(odb.arg.passing_args), False)


def get_att_chip_mac(target_port):
    comm_str = " --port %s read_mac" % (target_port)
    return run_esptool(comm_str, True).split("MAC: ")[1].strip().split("\n")[0].strip()


def get_chip_id(target_port):
    comm_str = " --port %s chip_id" % (target_port)
    raw_output = run_esptool(comm_str, True)
    if "Chip ID:" not in raw_output:
        print(magenta("Attach a development board to retrive the necesarry data"))
        print(yellow(raw_output))
        sys.exit(42)

    return raw_output.split("Chip ID: ")[1].split("\n")[0].strip()


def get_ports_list():
    with quiet():
        ports_list = local("ls /dev/ttyUSB*", capture=True).strip().split()
    if len(ports_list) == 0:
        print("\n", magenta("No compatible port detected"), "\n")
    return ports_list
