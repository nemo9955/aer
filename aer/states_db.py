from __future__ import absolute_import, division, print_function

import os
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.colors import blue, cyan, green, magenta, red, white, yellow

from utils import EasyDict, RecursiveFormatter

# pylint: disable=I0011,E1129


odb = EasyDict()

odb.boards_db = EasyDict()
odb.cache = EasyDict()
odb.run = EasyDict()

odb.arg = EasyDict()
odb.var = EasyDict()
odb.var.auto_detect = True
odb.var.flash_baud = 115200
odb.var.serial_baud = 115200


odb.env = EasyDict()
odb.env.skip_bad_hosts = True
odb.env.colorize_errors = True
odb.env.combine_stderr = True
odb.env.skip_unknown_tasks = True
odb.env.warn_only = True
odb.env.timeout = 5

odb.pth = EasyDict()
odb.pth.root = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "../.."))
odb.pth.user_db = os.path.join(odb.pth.root, "user_conf_db.json")
odb.pth.boards_db = os.path.join(odb.pth.root, "dev_boards_db.json")
odb.pth.cache_db = os.path.join(odb.pth.root, "cache_gen_db.json")
odb.pth.file_dbs = [
    odb.pth.user_db,
    odb.pth.boards_db,
    odb.pth.cache_db
]

odb.pth.trd_party = os.path.join(odb.pth.root, "3rd-party")
odb.pth.backup = os.path.join(odb.pth.root, "backup")
odb.pth.os_img_dir = os.path.join(odb.pth.root, "os-images")
odb.pth.trd_deploy_libs = os.path.join(odb.pth.trd_party, "deploy-libs")
odb.pth.trd_sketch_libs = os.path.join(odb.pth.trd_party, "sketch-libs")
odb.pth.esptool_py = os.path.join(
    odb.pth.trd_deploy_libs, "esptool/esptool.py")

odb.pth.include_libs = [
    os.path.join(odb.pth.trd_sketch_libs)
]
odb.pth.docker_containers_root = [
    os.path.join(odb.pth.root, "aer-components")
]

odb.dft = EasyDict()

odb.BOARD_SPECIFIC_VARS = EasyDict()
odb.dft.BOARD_SPECIFIC_VARS = EasyDict({
    "CHIP_LAST_HOSTNAME": "esp-{CHIP_ID_SHORT}",
})

odb.EXTRA_BUILD_FLAGS = EasyDict()
odb.dft.EXTRA_BUILD_FLAGS = EasyDict({
    "_S_WIFI_SSID": None,
    "_S_WIFI_PASS": None,
    "_S_OTA_HTTP_PATH": None,
    "_S_OTA_HTTP_USER": None,
    "_SERVER_IP": None,
    "_SERVER_PORT": None,
    "_S_OTA_HTTP_PASS": None
})

odb.boards_db = EasyDict()
odb.dft.boards_types = EasyDict({
    "esp8266": ["d1_mini", "d1_mini_lite", "d1_mini_pro", ],
    "esp32": ["lolin32", "esp32thing"]
})

odb.dft.boards_db = EasyDict({
    "esp8266": {
        "EXTRA_BUILD_FLAGS": {
        },
        "BOARD_SPECIFIC_VARS": {
        },
        "HTTP_ADDR": "{BOARD_SPECIFIC_VARS.CHIP_LAST_HOSTNAME}.local",
        "HTTP_URI": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_PATH}",
        "HTTP_PWD": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_PASS}",
        "HTTP_USR": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_USER}",
        "BOARD": "d1_mini",
        "VARIANT": "esp8266",
        "CHIP": "esp8266",
        "DESCRIPTION": "generic",
        "UPLOAD_SPEED": "921600",
        # "UPLOAD_SPEED": "460800",
        # "FLASH_DEF": "4M1M",
        # "SPIFFS_SIZE ": None,
        "UPLOAD_SPEED__": "460800"
    },
    "esp32": {
        "BOARD_SPECIFIC_VARS": {
        },
        "EXTRA_BUILD_FLAGS": {
        },
        "HTTP_ADDR": "esp-{CHIP_ID_SHORT}.local",
        "HTTP_URI": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_PATH}",
        "HTTP_PWD": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_PASS}",
        "HTTP_USR": "{EXTRA_BUILD_FLAGS._S_OTA_HTTP_USER}",
        "BOARD": "esp32thing",
        "VARIANT": "esp32",
        "CHIP": "esp32",
        "DESCRIPTION": "generic",
        "UPLOAD_SPEED": "921600",
        "UPLOAD_SPEED__": "460800",
    }
}
)

odb.dft.lib_proj = EasyDict({
    "url": None,
    "folder": None,
    "after_command": None,
    "validate_latest": None,
    "obtain_type": "git_clone",
    "download_url": "{url}",
    "get_command": "git clone {url} {folder}",
    "push_command": "git push",
    "update_command": "git pull",
    "slow": False,
    "can_push": False,
    "root_path": None
})


odb.libs_manager = EasyDict({
    "_transfer_type_": "update",
})

odb.libs_manager.NODE_BUILD_LIBS = EasyDict({
    "pth_full": None,
    "_transfer_type_": "update",
    "pth_alias": "trd_deploy_libs",
    "git_repo": [
        {
            "url": "git@github.com:esp8266/Arduino",
            "folder": "esp8266",
            "after_command": " cd esp8266/tools && python get.py "
        },
        {
            "url": "git@github.com:wemos/Arduino_XI.git",
            "folder": "XI",
            "after_command": "pwd && cd XI/ && sed -i 's/lgt8fx8e\\\\optiboot_lgt8f328d.hex/lgt8fx8e\/optiboot_lgt8f328d.hex/g' boards.txt "
        },
        {
            "url": "git@github.com:espressif/arduino-esp32.git",
            "folder": "esp32",
            "after_command": " cd esp32 && git submodule update --init --recursive && cd tools && python get.py "
        },
        # {"url": "git@github.com:thunderace/Esp8266-Arduino-Makefile.git",
        #     "folder": "Esp8266-Arduino-Makefile",
        #     "after_command": " sudo apt-get install libconfig-yaml-perl unzip sed git python  "
        #  },
        {"url": "git@github.com:plerup/makeEspArduino.git",
            "folder": "makeEspArduino"},
        # {"url": "git@github.com:Superhouse/esp-open-rtos.git", "folder": "esp-open-rtos",
        #     "get_command": " git clone --recursive  {url} {folder}"},
        # {"url": "git@github.com:pfalcon/esp-open-sdk.git", "folder": "esp-open-sdk", "slow": True,
        #     "get_command": "  git clone --recursive  {url} {folder} ",
        #     "update_command": " make clean && git pull && git submodule sync && git submodule update --init && make",
        #     "after_command": "  sudo apt-get install make unrar-free autoconf automake libtool gcc g++ gperf flex bison texinfo gawk ncurses-dev libexpat-dev python-dev python python-serial sed git unzip bash help2man wget bzip2 libtool-bin"
        #  },
        # {"url": "git@github.com:espressif/ESP8266_RTOS_SDK.git",
        #     "folder": "esp-rtos-sdk"},
        {"url": "git@github.com:espressif/esptool ",
         "folder": "esptool",
            "after_command": " sudo pip3 install pyserial  "
         }
    ]
})

odb.libs_manager.GOOGLE_PROTOBUF_1 = EasyDict({
    "pth_alias": "trd_party",
    "_transfer_type_": "overwrite",
    "git_repo": [
        {
            "url": "git@github.com:google/protobuf.git",
            "download_url": "https://github.com/google/protobuf",
            "obtain_type": "github_latest",
            "after_command": "test -e protoc-*.zip && unzip protoc-*.zip -d {folder} && rm protoc-*.zip ",
            "validate_latest": "/google/protobuf/releases/download/\S*/protoc-\S*linux-x86_64\\.zip",
            "folder": "google_protoc"
        }
    ]
})

odb.libs_manager.NANOPB_PROTOBUF_1 = EasyDict({
    "pth_alias": "trd_party",
    "_transfer_type_": "overwrite",
    "git_repo": [
        {
            "url": "https://github.com/nanopb/nanopb",
            "download_url": "https://jpa.kapsi.fi/nanopb/download/nanopb-0.3.9-linux-x86.tar.gz",
            "obtain_type": "wget_direct",
            "update_command": " ",
            "after_command": "cd {root_path} && test -e nanopb-*.tar.gz && mkdir -p {folder} && rm -rf {folder}/*  && tar -xzf nanopb-*.tar.gz -C {folder} && mv {folder}/nanopb*/* {folder}/  && rm nanopb-*.tar.gz ",
            "folder": "nanopb_protobuf"
        }
    ]
})

odb.libs_manager.NANOPB_PROTOBUF_1 = EasyDict({
    "pth_alias": "root",
    "_transfer_type_": "update",
    "git_repo": [
        {
            "url": "https://github.com/kashimAstro/SimpleNetwork",
            "get_command": "git clone {url} {folder} && cd {folder} && mv .git __GIT_IGNORE_GIT",
            "push_command": " ",
            "update_command": " cd {folder} && mv __GIT_IGNORE_GIT .git && git pull && mv .git __GIT_IGNORE_GIT",
            "folder": "RespirMesh/SimpleNetwork"
        }
    ]
})


odb.libs_manager.DEV_LIBS_PUSH = EasyDict({
    "pth_alias": "root",
    "can_push": True,
    "_transfer_type_": "update",
    "git_repo": [
        {"url": "git@github.com:nemo9955/aer.git",
            "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:nemo9955/aer.git",
            "folder": "aer"},
        {"url": "git@github.com:nemo9955/aer-components.git",
            "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:nemo9955/aer-components.git",
            "folder": "aer-components"},
        {"url": "git@github.com:nemo9955/RespirMesh.git",
            "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:nemo9955/RespirMesh.git",
            "folder": "RespirMesh"},
        {"url": "git@github.com:nemo9955/EspCar.git",
            "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:nemo9955/EspCar.git",
            "folder": "EspCar"}
    ]
})


odb.libs_manager.ARDU_NEEDED_LIBS = EasyDict({
    "pth_full": odb.pth.trd_sketch_libs,
    "pth_alias": None,
    "_transfer_type_": "update",
    "git_repo": [
        {
            "url": "git@github.com:bblanchon/ArduinoJson",
            "folder": "ArduinoJson",
            # "get_command": "exit 1",
            # "after_command": " test -e ArduinoJson*.zip && unzip ArduinoJson*.zip && rm ArduinoJson*.zip ",
            # "update_command": " ",
            # "validate_latest": "/bblanchon/ArduinoJson/releases/download/.*/ArduinoJson.*\\.zip"
        },
        # {"url": "",
        #     "folder": ""},
        # {"url": "git@github.com:marvinroger/async-mqtt-client",
        #     "folder": "async-mqtt-client"},
        # {"url": "git@github.com:baruch/esp8266_smart_home",
        #     "folder": "esp8266_smart_home"},
        {"url": "git@github.com:arkhipenko/TaskScheduler",
            "folder": "TaskScheduler"},
        {"url": "git@github.com:nanopb/nanopb",
            "after_command": " cd nanopb && rm -rf dist tests examples ",
            "folder": "nanopb"
         },
        {"url": "git@github.com:me-no-dev/ESPAsyncWebServer",
            "folder": "ESPAsyncWebServer"},
        {"url": "git@github.com:me-no-dev/AsyncTCP",
            "folder": "AsyncTCP"},
        {"url": "git@github.com:me-no-dev/ESPAsyncTCP",
            "folder": "ESPAsyncTCP"},
        # {"url": "git@github.com:AndreaLombardo/L298N",
        #     "folder": "arduino_L298N"},
        {"url": "git@github.com:PaulStoffregen/OneWire.git",
            "folder": "OneWire"},
        # {"url": "git@github.com:morrissinger/ESP8266-Websocket",
        #     "folder": "ESP-Websocket"},
        {"url": "git@github.com:Links2004/arduinoWebSockets.git",
            "folder": "WebSockets"},
        # {"url": "git@github.com:jasoncoon/esp8266-fastled-webserver.git",
        #     "folder": "fastled-webserver"},
        # {"url": "git@github.com:FastLED/FastLED.git",
        #     "folder": "FastLED"},
        # {"url": "git@github.com:sebastienwarin/IRremoteESP8266.git",
        #     "folder": "IRremoteESP8266"},
        # {"url": "git@github.com:adafruit/Adafruit_NeoPixel.git",
        #     "folder": "Adafruit_NeoPixel"},
        # {"url": "git@github.com:claws/BH1750.git",
        #     "folder": "BH1750-GY30"},
        # {"url": "git@github.com:milesburton/Arduino-Temperature-Control-Library.git",
        #     "folder": "Arduino-Temperature-Control-Library"},
        # {"url": "https://gitlab.com/painlessMesh/painlessMesh",
        #     "folder": "PainlessMesh"},
        # {"url": "git@github.com:adafruit/Adafruit-BMP085-Library.git",
        #     "folder": "Adafruit-BMP085"},
        # {"url": "git@github.com:adafruit/DHT-sensor-library.git",
        #     "folder": "DHT-sensor"},
        # {"url": "git@github.com:adafruit/Adafruit_Sensor.git",
        #     "folder": "Adafruit_Sensor"},
        {"url": "git@github.com:dancol90/ESP8266Ping",
            "folder": "ESP8266Ping"}
    ]
})
