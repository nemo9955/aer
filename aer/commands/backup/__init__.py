from __future__ import division, print_function

import argparse

# from aer.api import *
from aer.commands.backup.backup import entrypoint

 #pylint: disable=I0011,E1129




def init(parent_parser):
    bkParser = parent_parser.add_parser(
        'bk', help='Sub-command for backup and restore of different components ', conflict_handler='resolve')  # add_help=False,
    bkParser.set_defaults(entrypoint=entrypoint)

    target_group = bkParser.add_argument_group("Targeting")
    target_group.add_argument('-a', "--alias-config",
                              help='Select config from alias')
    target_group.add_argument('-t', "--target_host",
                              help='Specify exact host to deploy the containers to.')

    common_group = bkParser.add_argument_group("Common")

    bk_strategy = common_group.add_mutually_exclusive_group()
    bk_strategy.add_argument(
        "-l2", "--last-two", action="store_true", help="Backup the last 2 time sequences")
    bk_strategy.add_argument(
        "-fr", "--full-range", action="store_true", help="Backup all the time sequences")

    common_group.add_argument('-k', '--keywords', nargs='*', default=[],
                              help="List of keywords that must apear in the restored file name ")
    common_group.add_argument("-e", "--enumerate-files",
                              action="store_true", help="List all bacuped files, complies to 'keywords' ")

    gr_influxdb = bkParser.add_argument_group("Influxdb")
    gr_influxdb.add_argument("-ib", "--influxdb-backup",
                             action="store_true", help="InfluxDB backup")
    gr_influxdb.add_argument("-ir", "--influxdb-restore",
                             action="store_true", help="InfluxDB restore")

    gr_grafana = bkParser.add_argument_group("Grafana")
    gr_grafana.add_argument("-gb", "--grafana-backup",
                            action="store_true", help="Grafana backup")
    gr_grafana.add_argument("-gr", "--grafana-restore",
                            action="store_true", help="Grafana restore")
