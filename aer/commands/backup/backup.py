
# encoding=utf8
from __future__ import absolute_import, division, print_function

import calendar
import csv
import datetime
import json
import os
import sys
import time
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.api import *
from fabric.api import get
from fabric.colors import blue, cyan, green, magenta, red, white, yellow
from fabric.contrib import files
from fabric.contrib.console import confirm
from fabric.contrib.files import exists as texists

from aer import utils
# from aer.api import *
from states_db import odb
from utils import EasyDict, RecursiveFormatter

# pylint: disable=I0011,E1129


# reload(sys)
# sys.setdefaultencoding('utf8')


BACKUP_INFO = EasyDict()
BACKUP_INFO.influx_PPS = "7000"
BACKUP_INFO.influx_bk_container = "/backup/influxdb"
BACKUP_INFO.influx_bk_target = "~/backup/influxdb"
BACKUP_INFO.influx_export_file = "{database}_{host_id}_{file_year}-{file_month}_{backup_status}.{extension}"
BACKUP_INFO.grafana_export_file = "{grafana_type_export}_{datasource_name}_{file_year}-{file_month}.json"
BACKUP_INFO.dexec = "docker exec "


def entrypoint():
    config.handle()
    BACKUP_INFO.host_id = run("hostname").strip()

    if odb.arg.enumerate_files:
        list_all_files()

    if odb.arg.influxdb_backup:
        try:
            influxdb_backup()
        finally:
            pass
            # run("rm -rf ~/backup/influxdb ")
            # run("docker exec influxdb rm -rf /backup ")

    if odb.arg.influxdb_restore:
        try:
            influxdb_restore()
        finally:
            pass
            # run("rm -rf ~/backup/influxdb ")
            # run("docker exec influxdb rm -rf /backup ")

    if odb.arg.grafana_backup:
        grafana_backup()

    if odb.arg.grafana_restore:
        try:
            grafana_restore()
        finally:
            run("rm -rf ~/backup/grafana ")


def list_all_files():
    filter_backup_files(odb.pth.backup, print_info=True)


def influxdb_backup():
    influx_bk_local = pjoin(odb.pth.backup, "influxdb")
    local("mkdir -p {}".format(influx_bk_local))

    all_databases = get_databases()
    for db_ in all_databases:
        if db_ == "_internal":
            continue
        influxdb_export_points(db_, influx_bk_local)


def influxdb_export_points(database, backup_root, compress=True):
    dat = EasyDict()
    com = RecursiveFormatter(dat, BACKUP_INFO)
    dat.database = database
    dat.cont_name = "influxdb"
    dat.extension = "gz" if compress == True else "txt"
    dat.compress = "-compress" if compress == True else ""
    dat.root_data = "/data"
    with quiet():
        if run(com.raw_("{dexec} {cont_name} test -d {root_data}/data")).failed:
            dat.root_data = "/var/lib/influxdb"
        if run(com.raw_("{dexec} {cont_name} test -d {root_data}/data")).failed:
            print(red("Did not find root folder for influxdb ./data and ./wal"))
            return  # TODO Maybe something to improve
    dat.export_influx = "{dexec} {cont_name} influx_inspect export " + \
                        " -database {database} -datadir {root_data}/data -waldir {root_data}/wal {compress} " + \
                        " -start {start_date_iso} -end {end_date_iso} -out  {influx_bk_container}/{influx_export_file} "

    strategy = "last_two" if odb.arg.last_two else "full_range"
    sections_info = influx_section_database_time(database, strategy)

    # for seq_ in sections_info:
    #     print()
    #     print( seq_.start)
    #     print( seq_.end)

    # return

    run(com.raw_("mkdir -p {influx_bk_target}"))
    run(com.raw_("{dexec} {cont_name} mkdir -p {influx_bk_container}  "))

    # show("stdout")
    for seq_ in sections_info:
        dat.start_date_iso = seq_.start.isoformat() + "Z"
        dat.end_date_iso = seq_.end.isoformat() + "Z"
        dat.backup_status = seq_.status if "status" in seq_ else "full"
        dat.file_month = seq_.start.month
        dat.file_year = seq_.start.year

        influxdb_handle_exported(com, backup_root)


def influx_section_database_time(database, strategy="full"):
    start_date = start_date_influxdb(database)
    if start_date is None:
        print(red("Did not find a valid starting date for database " + database))
        return []
    time_seq = []

    start_date = start_date.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    while start_date < datetime.datetime.now():
        end_date = (start_date + datetime.timedelta(35)
                    ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        tslice = EasyDict()
        tslice.start = start_date
        tslice.end = end_date
        tslice.database = database
        tslice.status = "full"
        time_seq.append(tslice)
        start_date = end_date

    time_seq[0].status = "start"
    time_seq[-1].status = "part"
    if strategy == "last_two":
        return time_seq[-2:]
    return time_seq


def start_date_influxdb(database):
    db_tss = get_db_query("select * from /.*/ limit 5",
                          database=database, column="time")
    lst_ts = [t_ for t_ in db_tss if int(t_) > 1000]
    if len(lst_ts) == 0:
        return None

    min_ts_str = int(min(lst_ts)) / 1000000000
    start_date = datetime.datetime.fromtimestamp(min_ts_str)
    start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return start_date


def influxdb_handle_exported(com, backup_root):
    # print( "----------- +++++++++++++ -----------------------")
    # print( com.export_influx)
    # return
    # run(com.raw_("docker exec influxdb touch /{bk_fo lder}/{influx_export_file}"))
    run(com.export_influx)

    # TODO  check if it exists on local/central backup

    step_ok = True
    if not texists(com.raw_("{influx_bk_target}/{influx_export_file}")):
        step_ok = run(com.raw_(
            "docker cp influxdb:{influx_bk_container}/{influx_export_file} {influx_bk_target}/. ")).succeeded
        print(yellow("cont to target : " + str(step_ok)))
        run(com.raw_(
            "{dexec} {cont_name} rm -rf {influx_bk_container}/{influx_export_file}"))

    if step_ok:
        target_bk_path = com.raw_("{influx_bk_target}/{influx_export_file}")
        step_ok = get(remote_path=target_bk_path,
                      local_path=backup_root).succeeded
        print(yellow("target to local : " + str(step_ok)))

    if step_ok:
        step_ok = run(
            com.raw_("rm -rf {influx_bk_target}/{influx_export_file}")).succeeded
        print(yellow("delete from target : " + str(step_ok)))


def grafana_backup():
    influx_bk_local = pjoin(odb.pth.backup, "grafana")
    local_bk_datasource = pjoin(influx_bk_local, "datasource")
    local_bk_board = pjoin(influx_bk_local, "dashboard")

    grafana_retrive_datasources(local_bk_datasource)
    grafana_retrive_dashboards(local_bk_board)


def grafana_restore():
    influx_bk_local = pjoin(odb.pth.backup, "grafana")
    run("mkdir -p ~/backup/grafana/datasource ")
    run("mkdir -p ~/backup/grafana/dashboard ")
    put(os.path.join(influx_bk_local, "datasource/*"),
        "~/backup/grafana/datasource")
    put(os.path.join(influx_bk_local, "dashboard/*"),
        "~/backup/grafana/dashboard")

    target_bk_datasource = "~/backup/grafana/datasource"
    target_bk_board = "~/backup/grafana/dashboard"

    restore_dashboards(target_bk_board)
    restore_datasources(target_bk_datasource)


def restore_datasources(root_folder):
    grafana_url = "localhost:3000"
    with hide('running'):
        ds_fils = run("ls -1 {}/*.json".format(root_folder)
                      ).replace("\r", "").split("\n")
        for dast in ds_fils:
            print(dast)
            run(' curl -X POST -H "Content-Type: application/json" ' +
                '-d @{} http://{}:{}@{}/api/datasources '.format(
                    dast, odb.var.GRAFANA_ADMIN_NAME, odb.var.GRAFANA_ADMIN_PASS, grafana_url))


def restore_dashboards(root_folder):
    grafana_url = "localhost:3000"
    # grafana_url = "localhost/grafana"
    db_fils = run("ls -1 {}/*.json".format(root_folder)
                  ).replace("\r", "").split("\n")
    for dash_name in db_fils:
        with hide('output'):
            json_data = run("cat '" + dash_name + "'").strip()
        d_file = json.loads(json_data)

        # if "dashboard" in d_file and "id" in d_file["dashboard"]:
        #     d_file["dashboard"]["id"] = "null"

        dash_type = "db"
        if "title" in d_file and d_file["title"] == "Home":
            dash_type = "home"

        # with hide('running'):
        run(' curl -X POST -H "Content-Type: application/json" -d @{} http://{}:{}@{}/api/dashboards/{}   ' .format(
            dash_name, odb.var.GRAFANA_ADMIN_NAME, odb.var.GRAFANA_ADMIN_PASS, grafana_url, dash_type))

    print(db_fils)


def grafana_retrive_dashboards(parent_local_folder):
    local("mkdir -p " + parent_local_folder)
    dashds = json.loads(
        run("curl http://localhost/grafana/api/search/ ").strip())

    for db_ in dashds:
        print(db_)
        bd_pth = "http://localhost/grafana/api/dashboards/" + db_["uri"]
        write_dashboard(bd_pth, parent_local_folder)


def write_dashboard(get_path, parent_folder, isHome=False):
    dat = EasyDict()
    com = RecursiveFormatter(dat, BACKUP_INFO)

    raw_dbdi = json.loads(run("curl " + get_path))
    the_db = raw_dbdi["dashboard"]
    the_db.pop("version", None)
    the_db.pop("id", None)

    good_from = {}
    good_from["dashboard"] = the_db
    good_from["overwrite"] = True

    dat.grafana_type_export = "dashboard"
    dat.file_month = datetime.datetime.now().month
    dat.file_year = datetime.datetime.now().year
    dat.datasource_name = raw_dbdi["meta"]["slug"]

    # db_fn = (str(raw_dbdi["meta"]["slug"]) + "_dashboard.json")

    if isHome == True:
        # db_fn = "HOME-dashboard.json"
        dat.datasource_name = "_HOME_"
        good_from["meta"] = {"isHome": True}

    datasource_bk_path = com.raw_(
        pjoin(parent_folder, BACKUP_INFO.grafana_export_file))

    with open(datasource_bk_path, "w") as dbo:
        json.dump(good_from, dbo)


def grafana_retrive_datasources(parent_local_folder):
    dat = EasyDict()
    com = RecursiveFormatter(dat, BACKUP_INFO)
    dat.grafana_type_export = "datasource"

    dat.file_month = datetime.datetime.now().month
    dat.file_year = datetime.datetime.now().year
    with quiet():
        # TODO in case values are not found, prompt user for them !!!!, Maybe
        # generalize the procedure
        dasource = json.loads(run("curl http://{}:{}@localhost/grafana/api/datasources/ ".format(
            odb.var.GRAFANA_ADMIN_NAME, odb.var.GRAFANA_ADMIN_PASS)).strip())

    local("mkdir -p " + parent_local_folder)
    for datas_dict in dasource:
        dat.datasource_name = datas_dict["name"]

        datasource_bk_path = com.raw_(
            pjoin(parent_local_folder, BACKUP_INFO.grafana_export_file))
        datas_dict.pop("id", None)

        with open(datasource_bk_path, "w") as das:
            json.dump(datas_dict, das)


def influxdb_restore():
    influx_bk_local = pjoin(odb.pth.backup, "influxdb")
    influxdb_restore_points(influx_bk_local)


def influxdb_restore_points(restore_root, compressed=True):
    dat = EasyDict()
    com = RecursiveFormatter(dat, BACKUP_INFO)

    dat.restore_root = restore_root
    dat.cont_name = "influxdb"
    dat.extension = "gz" if compressed else "txt"
    dat.compressed = "-compressed" if compressed else ""
    dat.import_influxdb = "{dexec} {cont_name} influx -import -pps {influx_PPS} " + \
        " -path={container_file_path} {compressed} "

    files_list = filter_backup_files(restore_root, print_info=True)

    if not confirm("Do you want to continue ?"):
        return

    run(com.raw_("mkdir -p {influx_bk_target} "))
    run(com.raw_("{dexec} {cont_name}  mkdir -p {influx_bk_container} "))

    for file_ in files_list:
        local_file_path = pjoin(restore_root, file_)
        dat.file_name = file_
        dat.target_file_path = com.raw_("{influx_bk_target}/{file_name}")
        dat.container_file_path = "{influx_bk_container}/{file_name}"
        # if not texists(dat.target_file_path):
        l_to_t = put(local_file_path, dat.target_file_path)
        # if l_to_t.failed:
        #     continue

        t_to_c = run(
            com.raw_("docker cp {target_file_path} {cont_name}:{influx_bk_container}/."))
        # if t_to_c.failed:
        #     continue
        # TODO if there are failed points , retry the precedure
        try_again = run(com.import_influxdb).failed
        if try_again:
            dat.influx_PPS = "3000"
            run(com.import_influxdb)
            dat.influx_PPS = "7000"

        print()
        print(com.raw_(dat.import_influxdb))
        print()


def filter_backup_files(restore_root, additional_kw=[], print_info=False):
    to_exclude = additional_kw
    to_exclude.extend(odb.arg.keywords)

    rtor_files = utils.all_subfiles(restore_root, remove_root_str=True)
    rtor_files = utils.elements_contain(rtor_files, to_exclude)

    if print_info:
        print(green("Restored path must contain words :"))
        print("\t", "\n\t".join(to_exclude))

        print(green("Backups to be restored :"))
        print("\t", "\n\t".join(rtor_files))
        print()

    return rtor_files


def get_points_info():
    meas_count = get_db_query("SHOW MEASUREMENTS", database=database)
    total_points = 0
    # for mea_ in meas_count:
    points_count = get_db_query(
        u"select count(*) from /.*/ ", database=database, column="count_value")
    # where time > \'{start_date_iso}\' and time <  \'{end_date_iso}\'
    print("points_count", points_count)
    # total_points += int(points_count[0]) if len(points_count)>0  and int(points_count[0]) < 100000000 else 0
    total_points = sum([int(i) for i in points_count])
    print("total_points", total_points)
    print()
    print("min_ts_str", min_ts_str)
    print("time.time()", time.time())
    print()
    total_days = datetime.timedelta(
        float(time.time() - min_ts_str) / 60 / 60 / 24).days
    print("total_days", total_days)
    print()
    point_10k_ratio = float(total_points / 10000.0)
    print("point_10k_ratio", point_10k_ratio)
    print("total_days/point_10k_ratio", total_days / point_10k_ratio)
#       1498110279
#       1513760269.65


# def extract_influx_to_csv(database, local_bk_dir):
#     influx_bk_command = " \' -format csv -execute \\\'select * from \"{}\" LIMIT 10 \\\' -database \"{}\" \' > exported_csv/{}/{} "
#     docker_bk_command = "docker exec influxdb influx {} ".format(influx_bk_command)
#     print()
#     print( docker_bk_command)
#     print()
#     measurm_list = get_db_query("SHOW MEASUREMENTS", database=database)

#     db_exp_pth = pjoin("backup/influxdb/exported_csv", database)
#     run("mkdir -p " + db_exp_pth)

#     for meas_ in measurm_list:
#         print( meas_)
#         csv_fn = "%s_%s_%s.csv" % (
#             utils.make_safe_str(meas_),
#             str(int(time.time())),
#             run("hostname").strip()
#         )

#         bk_command = docker_bk_command.format(meas_, database, database, csv_fn)
#         expres = run(bk_command)

#     local("mkdir -p " + pjoin(local_bk_dir, database))
#     get(remote_path=db_exp_pth, local_path=local_bk_dir)
#     # continue

try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO


def get_db_query(db_query,  database=None, column="name"):
    query_command = u"docker exec influxdb influx -execute '{}' -format 'csv' ".format(
        db_query.replace("\'", "\'\"\'\"\'"))

    if database is not None:
        query_command += " -database {} ".format(database)

    with hide('output'):
        query_str = run(query_command)

    if len(query_str.strip()) == 0:
        return []

    reader = csv.DictReader(StringIO(query_str), delimiter=',')
    all_databases = []
    for row in reader:
        if column not in row or row[column] == column:
            continue
        if len(row[column]) == 0:
            continue
        all_databases.append(row[column])
    return all_databases


def get_databases():
    return get_db_query("SHOW DATABASES", column="name")
