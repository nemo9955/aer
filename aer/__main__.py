from __future__ import division, print_function

import os
import sys

import file_db_handler

try:
    from fabric.api import env
except:
    print( 'Main dependencies !!')
    print( 'sudo usermod -a -G dialout $USER')
    print( 'Fabric3 not installed')
    print( 'sudo apt-get install python3-pip')
    print( 'sudo python3 -m pip install --upgrade pip setuptools pyserial Fabric3')
    sys.exit(85)


# pylint: disable=I0011,E1129

imp_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(imp_path)


file_db_handler.handle()
