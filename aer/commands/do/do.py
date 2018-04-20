from __future__ import absolute_import, division, print_function

import datetime
import os
import re
import uuid
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import *
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

# from aer.api import *
from states_db import odb
from utils import EasyDict, RecursiveFormatter
from aer.commands.component import util as cutil

# from aer.states_db import odb

# pylint: disable=I0011,E1129


def entrypoint():
    if odb.arg.docker and cutil.docker_not_installed():
        cutil.install_docker()

    if odb.arg.rm_all_containers:
        run("docker stop $(docker ps -a -q)")
        run("docker rm $(docker ps -a -q)")

    if odb.arg.rm_all_images:
        run("docker rmi $(docker images -a -q)")

    if odb.arg.rm_all_volumes:
        run("docker volume rm $(docker volume ls -f dangling=true -q)")
    # if odb.arg.regenerate_db:
    #     local("rm " + odb.pth.user_db)
    #     local("rm " + odb.pth.cache_db)
    #     from aer import file_db_handler
    #     file_db_handler.generate_user_db()

    if odb.arg.build_protobuf:
        local("cd {0}/RespirMesh/protobuf && mkdir -p rem_nanopb_pb  && {0}/3rd-party/nanopb_protobuf/generator-bin/protoc  --nanopb_out=./rem_nanopb_pb *.proto ".format(odb.pth.root))
        go_ok = local(
            "cd {0}/RespirMesh/protobuf && mkdir -p rem_go_pb && {0}/3rd-party/google_protoc/bin/protoc --go_out=./rem_go_pb  *.proto ".format(odb.pth.root)).succeeded
        if not go_ok:
            print(cyan("Maybe run"))
            print(yellow("export GOPATH=$HOME/gopath"))
            print(yellow("export PATH=$PATH:/usr/local/go/bin:$GOPATH/bin"))
            print(yellow("go get -u github.com/golang/protobuf/protoc-gen-go"))
        local("cp {0}/RespirMesh/protobuf/rem_nanopb_pb/*  {0}/RespirMesh/RespirMeshClient/examples/  ".format(odb.pth.root))
