
from __future__ import division, print_function

import copy
import os
import urllib
from os.path import join as pjoin

from fabric.api import *
from fabric.colors import blue, cyan, green, magenta, red, white, yellow

# pylint: disable=I0011,E1129


def make_safe_str(badString):
    return urllib.quote(badString.encode("utf-8")).replace("%", "_")
