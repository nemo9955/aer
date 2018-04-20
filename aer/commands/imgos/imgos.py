from __future__ import absolute_import, division, print_function

import os
import time
import uuid
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import (  fastprint, lcd, local, quiet, sudo)
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib.console import confirm

from aer import utils
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# from aer.states_db import odb

# pylint: disable=I0011,E1129


def entrypoint():
    target_out = select_card()
    if odb.arg.burn:
        target_image = select_image()
        burn_image(target_out, target_image, odb.arg.bs)

    if odb.arg.write or odb.arg.add_ssh:
        for parr in card_parts(target_out):
            temp = "$HOME/tmp/" + str(uuid.uuid4())
            local("sudo mkdir -p " + temp)
            local("sudo mount " + parr + " " + temp)
            try:
                with lcd(temp):
                    if odb.arg.add_ssh:
                        enable_ssh(parr)
                    if odb.arg.write:
                        write_to_part(parr)
            finally:
                local("sudo umount " + parr)
                local("sudo rm -rf " + temp)
                local("sync ")


def card_parts(sdcard_path):
    partitions = []
    fdisk_output = local("sudo fdisk -l " + sdcard_path, capture=True)
    for sep in fdisk_output.split():
        if sep.startswith(str(sdcard_path)) and os.path.exists(sep) and sep not in partitions:
            partitions.append(sep)
    return partitions


def enable_ssh(_partition):
    local("sudo touch ssh")
    local("test -e boot && sudo touch boot/ssh")
    # isBootPart = False
    # for line in local("ls -l /dev/disk/by-label", capture=True).split("\n"):
    #     lspl = line.split()
    #     print( lspl)
    #     if "boot" in lspl and _partition.split("/")[-1] in line:
    #         isBootPart = True
    #         break


# ip_push = "/usr/bin/curl -u \"o.\": https://api.pushbullet.com/v2/pushes -d type=note -d title=\"$(/bin/hostname) IP\" -d body=\"$(/bin/ip a)\""


src_list = """#deb http://mirrordirector.raspbian.org/raspbian/ jessie main contrib non-free rpi\n
# Uncomment line below then 'apt-get update' to enable 'apt-get source'\n
#deb-src http://archive.raspbian.org/raspbian/ jessie main contrib non-free rpi\n
\n
\n
deb http://mirror.ox.ac.uk/sites/archive.raspbian.org/archive/raspbian jessie main"""


def write_to_part(_partition):
    print(red(local("sudo find . -name .profile -type f  ")))
    if confirm("Delete all .profiles ?", default=False):
        local("sudo find . -name .profile -type f -delete ")

    # if "etc" in local("ls", capture=True).split("\n"):
    #     net_startup = "#!/bin/sh "
    #     net_startup += "\n\nif [[ `uptime -p | tr -dc '0-9'` -lt 20 ]] ; then "
    #     net_startup += "\n\n\t(/bin/sleep 10 && " + ip_push + " ) & "
    #     net_startup += "\n\nfi"
    #     net_startup += "\n\nexit 0"
    #     net_startup += "\n\n"
    #     oh_ns = "etc/network/if-up.d/aer-ap-netstart"

    #     local("echo \'" + net_startup + "\' | sudo tee " + oh_ns)
    #     local("sudo chmod 755 " + oh_ns)
    #     local("ls -al etc/network/if-up.d")
    #     if confirm("replace SOURCE List ?", default=False):
    #         local("echo \'" + src_list + "\' | sudo tee /etc/apt/sources.list ")


def burn_image(card_path, img_path, burn_bs):
    com = "sudo dd status=progress bs=" + burn_bs + \
        " if=" + img_path + " of=" + card_path

    print(cyan("The folowing command will be executed:"))
    print(cyan(com))

    if confirm("Do you want to continue ?",):
        local(com)
        local("sync")


def select_image():
    if odb.arg.ifl is not None:
        return odb.arg.ifl

    osi_path = odb.pth.os_img_dir
    osi_list = [osi for osi in utils.all_subfiles(osi_path)
                if osi.endswith(".img")]

    odb.arg.ifl = utils.pick_from_list(osi_list)
    return odb.arg.ifl


def select_card():
    if odb.arg.ofl is not None:
        return odb.arg.ofl

    keywordsSet = set(["MMC", "mmc", "card", "SDHC", "SD"])
    print("Please insert SD card now.")
    with quiet():
        str_time = str(local("dmesg|tail -n 1", capture=True)
                       ).strip().split("]")[0][1:]
        print(str_time)

        lastTimestamp = float(str_time)
    # lastTimestamp  = str(local("dmesg|tail -n 1",capture=True)).strip()
    print(lastTimestamp)

    sdPath = ""
    while sdPath == "":
        fastprint(".")
        time.sleep(1)
        with quiet():
            dmsgTail = local("dmesg|tail", capture=True).split("\n")
        # print( dmsgTail)
        possibleSDCard = False
        detectedActivity = False
        for i, row in enumerate(dmsgTail):
            ts = float(str(row).strip().split("]")[0][1:])
            if ts > lastTimestamp:
                rowList = row.replace(":", "").split()
                rowSet = set(rowList)

                if not detectedActivity:
                    detectedActivity = True
                    print("Detected activity.")
                    with quiet():
                        print(yellow(local("dmesg|tail -n 4", capture=True)))

                if not possibleSDCard:
                    if len(rowSet.intersection(keywordsSet)) == 0 or "removed" in rowSet:
                        lastTimestamp = ts
                        continue

                TEMPsdPath = pjoin("/dev", rowList[1].strip())

                if os.path.exists(TEMPsdPath):
                    print("Detected SD card.")
                    sdPath = TEMPsdPath
                    break
                else:
                    possibleSDCard = True

    odb.arg.ofl = sdPath
    return odb.arg.ofl


def update_local_imgs():
    pass
    # https://downloads.raspberrypi.org/raspbian_lite_latest
    # https://downloads.raspberrypi.org/raspbian_latest
