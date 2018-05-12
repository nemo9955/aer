
from __future__ import absolute_import, division, print_function

import os
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import cd, env, execute, quiet, run,put,local
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

from aer import  utils
from states_db import odb

# pylint: disable=I0011,E1129


def dev_type():
    with quiet():
        return str(run("uname -m")).strip()


def to_host(source, rename=None, exclude=[]):
    """
        TODO MAKE TESTS !!!!!
        Wrapper over fabric.api.put()
        Copies from localPath to hostPath
        If no destination specified, PWD will be used
        return boolean if files copied succesfully
    """
    exclude.extend([".", ".."])
    src_basename = os.path.basename(source)
    new_basename = rename or src_basename

    if os.path.isdir(source):
        # dir_content = local("ls -a " + source, capture=True).split()
        dir_content = local("ls -1 -a " + source,
                            capture=True).replace("\r", "").split("\n")
        run("mkdir -p " + new_basename)
        # run("pwd && ls -al ")
        # print( blue(dir_content))
        with cd(new_basename):
            for tmv in dir_content:
                if tmv in exclude:
                    continue
                # print( yellow(tmv))
                full_path = pjoin(source, tmv)
                put("%s" % (full_path), ".")
                # run("pwd && ls -al ")
        return True

    elif os.path.isfile(source):
        put(source, ".")
        mv_status = True
        if rename is not None:
            mv_status = run("mv " + src_basename + " " + rename).succeeded

        return mv_status

    print(magenta("No valid folder/file at path " + source))
    return False

def host_up(host_name):
    ret_msg = None
    with hide('running', 'stdout', "status", "warnings"):
        ret_msg = execute((lambda: run("hostname && pwd && users")), hosts=[
            host_name])[host_name]
    # print( "----------",type(ret_msg) , ret_msg)
    if isinstance(ret_msg, basestring):
        return True
    elif isinstance(ret_msg, Exception):
        return False
    else:
        print("!!!!\n!!!!!!!!\\n!!!!!!!!\n!!!!!!\n!!!!!!!!!\n!!!!!!!!\n!!!!!!\n!!!!!!!!!")
        print(ret_msg)
        return False


###################################################################
############### DOCKER ############################################
###################################################################

def docker_not_installed():
    with quiet():
        dout = run("docker").strip()
        return dout.endswith("command not found")


def install_docker():
    print(green("Instaling Docker."))
    stat_up = run("sudo apt-get update ")
    # sudo("apt-get upgrade")
    stat_do = update_docker()
    if stat_do.failed or stat_up.failed:
        return
    # operations.reboot()
    # run("systemctl start docker")
    run("sudo usermod -aG docker `whoami` ")


def update_docker():
    return run("curl -sSL https://get.docker.com | sh")

###################################################
###################################################
###################################################


def is_running(cont_name):
    with quiet():
        running = str(run("docker inspect -f {{.State.Running}} " + cont_name))
    if running == "true":
        return True
    else:
        return False


def ensure_cont_stopped(container_name):
    if is_running(container_name):
        with quiet():
            print(cyan("Stopping docker container {}".format(container_name)))
            run("docker stop %s" % container_name)
            run("docker rm -f %s" % container_name)


def create_storage_container(container_name):
    with quiet():
        if "Error" in run("docker volume inspect %s-storage 2>&1" % container_name):
            print(cyan("Creating docker volume {}-storage".format(container_name)))
            run("docker volume create --name %s-storage" % container_name)


def print_cont_status(container_name):
    runs = is_running(container_name)
    if runs:
        print(green(container_name + " is running !"))
    else:
        for i in range(5):
            print(red(container_name + " IS NOT RUNNING !!!!! ", bold=True), "\n")


def build_latest_image(container_name, container_image, cont_root=None):
    df_name = "Dockerfile-" + dev_type()
    if cont_root is None:
        cont_root = odb.cache.all_containers.get(container_name, "")

    if fexists(pjoin(cont_root, "Dockerfile")):
        to_host(pjoin(cont_root, "Dockerfile"))
        run(" docker build -t %s . " % (container_image))

    elif fexists(pjoin(cont_root, df_name)):
        to_host(pjoin(cont_root, df_name), rename="Dockerfile")
        run(" docker build -t %s . " % (container_image))


def ensute_custom_network_bridge():
    if odb.var.docker_network_name not in run("docker network ls"):
        run("docker network create " +
            # " --driver bridge " +
            " --subnet 192.168.59.0/8 {} ".format(odb.var.docker_network_name))


# if [[ -e $CURRENT_PATH/Dockerfile ]]; then
# 	echo "Building image for $CURRENT_PATH/Dockerfile "
# 	cd $CURRENT_PATH
# 	docker build -f $CURRENT_PATH/Dockerfile -t $GRAFANA_IMG_NAME .
# fi
