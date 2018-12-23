# pylint: disable=I0011,E1129,E0611
from __future__ import absolute_import, division, print_function

import os
from os.path import exists as fexists
from os.path import join as pjoin

from fabric.colors import blue, cyan, green, magenta, red, white, yellow

from utils import EasyDict, RecursiveFormatter, local_hostname

odb = EasyDict()

odb.boards_db = EasyDict()
odb.cache = EasyDict()
odb.run = EasyDict()

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
    # os.path.join(odb.pth.trd_sketch_libs),
    os.path.join(odb.pth.root, "RespirMesh/RemCppCommon"),
    os.path.join(odb.pth.root, "3rd-party/nanopb_protobuf"),
    os.path.join(odb.pth.root, "3rd-party/nanopb_protobuf/extra"),
    os.path.join(odb.pth.root, "RespirMesh/protobuf/rem_nanopb_pb"),
    os.path.join(odb.pth.root, "EspCar/src"),
]
odb.pth.docker_containers_root = [
    os.path.join(odb.pth.root, "aer-components")
]


odb.arg = EasyDict()
odb.var = EasyDict()
odb.var.auto_detect = True
odb.var.flash_baud = 115200
odb.var.serial_baud = 115200

odb.var.GRAFANA_ADMIN_NAME = "admin-graf"
odb.var.GRAFANA_ADMIN_PASS = "admin.pass"
odb.var.DEV_HOSTNAME = local_hostname()
odb.var.docker_network_name = "something"
odb.var.AP_SSID = "SOMEAP"
odb.var.AP_PASS = "someap.pass"
odb.var.HASS_CONFIG_PATH = os.path.join(odb.pth.root, "configuration.yaml")


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

odb.dft.libs_manager_to_proj = [
    "after_command", "obtain_type", "get_command", "push_command", "update_command"]

odb.dft.lib_proj = EasyDict({
    "url":    "https://github.com/{repo_path}",
    "folder": None,
    "after_command": None,
    "validate_latest": None,
    "obtain_type": "git_clone",
    "download_url": "{url}",
    "get_command": "git clone {url} {folder}",
    "push_command": "git push",
    "update_command": "git pull",
    "root_path": None,
    "tags": "",
})


odb.libs_manager = EasyDict({
    "_transfer_type_": "update",
})

odb.libs_manager.BOARDS_BUILD_LIBS = EasyDict({
    "pth_full": None,
    "_transfer_type_": "update",
    "pth_alias": "trd_deploy_libs",
    "tags": "build",
    "git_repo": [
        {
            "repo_path": "esp8266/Arduino",
            "folder": "esp8266",
            "after_command": " cd esp8266/tools && python get.py "
        },
        {
            "repo_path": "wemos/Arduino_XI",
            "folder": "XI",
            "after_command": "pwd && cd XI/ && sed -i 's/lgt8fx8e\\\\optiboot_lgt8f328d.hex/lgt8fx8e\/optiboot_lgt8f328d.hex/g' boards.txt "
        },
        {
            "repo_path": "espressif/arduino-esp32",
            "folder": "esp32",
            "after_command": " cd esp32 && git submodule update --init --recursive && cd tools && python get.py "
        },
        # {"repo_path":"thunderace/Esp8266-Arduino-Makefile",
        #     "folder": "Esp8266-Arduino-Makefile",
        #     "after_command": " sudo apt-get install libconfig-yaml-perl unzip sed git python  "
        #  },
        {"repo_path": "plerup/makeEspArduino",
            "folder": "makeEspArduino"},
        # {"repo_path":"Superhouse/esp-open-rtos", "folder": "esp-open-rtos",
        #     "get_command": " git clone --recursive  {url} {folder}"},
        # {"repo_path":"pfalcon/esp-open-sdk", "folder": "esp-open-sdk", "slow": True,
        #     "get_command": "  git clone --recursive  {url} {folder} ",
        #     "update_command": " make clean && git pull && git submodule sync && git submodule update --init && make",
        #     "after_command": "  sudo apt-get install make unrar-free autoconf automake libtool gcc g++ gperf flex bison texinfo gawk ncurses-dev libexpat-dev python-dev python python-serial sed git unzip bash help2man wget bzip2 libtool-bin"
        #  },
        # {"repo_path":"espressif/ESP8266_RTOS_SDK",
        #     "folder": "esp-rtos-sdk"},
        {"repo_path": "espressif/esptool ",
         "folder": "esptool",
         "tags": "esptool",
            # "update_command": "git checkout ee00d84 ",
            # "after_command": " cd {folder} && git checkout ee00d84 && sudo pip3 install pyserial  "
         }
    ]
})


odb.libs_manager.PROTOBUFFERS = EasyDict({
    "pth_alias": "trd_party",
    "_transfer_type_": "overwrite",
    "tags": "protobuf pbuf",
    "git_repo": [
        {
            "repo_path": "protocolbuffers/protobuf",
            "download_url": "https://github.com/protocolbuffers/protobuf",
            "update_command": "rm -rf {full_path} ",
            "tags": "slow",
            "obtain_type": "github_latest",
            "after_command": "test -e protoc-*.zip && unzip protoc-*.zip -d {folder} && rm protoc-*.zip ",
            "validate_latest": "/protocolbuffers/protobuf/releases/download/\S*/protoc-\S*linux-x86_64\\.zip",
            "folder": "protocolbuffers"
        },
        {
            "repo_path": "nanopb/nanopb",
            "download_url": "https://jpa.kapsi.fi/nanopb/download/nanopb-0.3.9.1-linux-x86.tar.gz",
            "tags": "slow",
            "obtain_type": "wget_direct",
            "update_command": "rm -rf {full_path} ",
            "after_command": "cd {root_path} && test -e nanopb-*.tar.gz && mkdir -p {folder} && rm -rf {folder}/*  && tar -xzf nanopb-*.tar.gz -C {folder} && mv {folder}/nanopb*/* {folder}/  && rm nanopb-*.tar.gz ",
            "folder": "nanopb_protobuf"
        }
    ]
})


odb.libs_manager.NEMO9955_LIBS_PUSH = EasyDict({
    "pth_alias": "root",
    "tags": "can_push push",
    "_transfer_type_": "update",
    "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:{repo_path}.git",
    "git_repo": [
        {"repo_path": "nemo9955/aer",
            "folder": "aer"},
        {"repo_path": "nemo9955/nodes-ourhab",
            # "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:{repo_path}.git",
            "folder": "nodes-ourhab"},
        {"repo_path": "nemo9955/aer-components",
            "folder": "aer-components"},
        {"repo_path": "nemo9955/RemPeripherals",
            "tags": "dependency dep filesystem",
            "folder": "RemPeripherals"},
        {"repo_path": "nemo9955/RespirMesh",
            "tags": "dependency dep filesystem",
            "folder": "RespirMesh"},
        {"repo_path": "nemo9955/EspCar",
            "tags": "dependency dep filesystem",
            # "after_command": "cd {folder} && ssh -T git@github.com 2>&1  | grep successfully && git remote set-url origin  git@github.com:{repo_path}.git",
            "folder": "EspCar"}
    ]
})

odb.libs_manager.NETWORK_LIBS = EasyDict({
    "pth_alias": "trd_party",
    "_transfer_type_": "overwrite",
    "tags": "network sockets",
    "git_repo": [
        {
            "repo_path": "dermesser/libsocket",
            "folder": "libsocket",
            "after_command": "cd {folder} && cmake CMakeLists.txt && make && make install "
        }
    ]
})

odb.libs_manager.ARDU_NEEDED_LIBS = EasyDict({
    "pth_full": odb.pth.trd_sketch_libs,
    "pth_alias": None,
    "tags": "dependency dep",
    "_transfer_type_": "update",
    "git_repo": [
        {
            "repo_path": "bblanchon/ArduinoJson",
            "folder": "ArduinoJson",
            # "get_command": "exit 1",
            # "after_command": " test -e ArduinoJson*.zip && unzip ArduinoJson*.zip && rm ArduinoJson*.zip ",
            # "update_command": " ",
            # "validate_latest": "/bblanchon/ArduinoJson/releases/download/.*/ArduinoJson.*\\.zip"
        },
        # {"url": "",
        #     "folder": ""},
        # {"repo_path":"marvinroger/async-mqtt-client",
        #     "folder": "async-mqtt-client"},
        # {"repo_path":"baruch/esp8266_smart_home",
        #     "folder": "esp8266_smart_home"},
        {"repo_path": "arkhipenko/TaskScheduler",
            "folder": "TaskScheduler"},
        {"repo_path": "nanopb/nanopb",
            "after_command": " cd nanopb ; rm -rf dist tests examples ",
            "update_command": "git pull && {after_command} ",
            "tags": "special",
            "folder": "nanopb"
         },
        {"repo_path": "wemos/LOLIN_HP303B_Library",
            "folder": "LOLIN_HP303B_Library"},
        {"repo_path": "wemos/WEMOS_DHT12_Arduino_Library",
            "folder": "WEMOS_DHT12_Arduino_Library"},
        {"repo_path": "adafruit/Adafruit_Sensor",
            "folder": "Adafruit_Sensor"},
        {"repo_path": "adafruit/Adafruit_SSD1306",
            "folder": "Adafruit_SSD1306"},
        {"repo_path": "adafruit/DHT-sensor-library",
            "folder": "DHT-sensor-library"},
        {"repo_path": "adafruit/Adafruit-GFX-Library",
            "folder": "Adafruit-GFX-Library"},
        {"repo_path": "adafruit/Adafruit_ILI9341",
            "folder": "Adafruit_ILI9341"},
        {"repo_path": "PaulStoffregen/XPT2046_Touchscreen",
            "folder": "XPT2046_Touchscreen"},
        {"repo_path": "wemos/D1_mini_Examples",
            "folder": "D1_mini_Examples"},
        {"repo_path": "me-no-dev/ESPAsyncWebServer",
            "folder": "ESPAsyncWebServer"},
        {"repo_path": "me-no-dev/AsyncTCP",
            "folder": "AsyncTCP"},
        {"repo_path": "me-no-dev/ESPAsyncTCP",
            "folder": "ESPAsyncTCP"},
        # {"repo_path":"AndreaLombardo/L298N",
        #     "folder": "arduino_L298N"},
        {"repo_path": "PaulStoffregen/OneWire",
            "folder": "OneWire"},
        # {"repo_path":"morrissinger/ESP8266-Websocket",
        #     "folder": "ESP-Websocket"},
        {"repo_path": "Links2004/arduinoWebSockets",
            "folder": "WebSockets"},
        # {"repo_path":"jasoncoon/esp8266-fastled-webserver",
        #     "folder": "fastled-webserver"},
        # {"repo_path":"FastLED/FastLED",
        #     "folder": "FastLED"},
        # {"repo_path":"sebastienwarin/IRremoteESP8266",
        #     "folder": "IRremoteESP8266"},
        # {"repo_path":"adafruit/Adafruit_NeoPixel",
        #     "folder": "Adafruit_NeoPixel"},
        {"repo_path":"claws/BH1750",
            "folder": "BH1750-GY30"},
        # {"repo_path":"milesburton/Arduino-Temperature-Control-Library",
        #     "folder": "Arduino-Temperature-Control-Library"},
        # {"url": "https://gitlab.com/painlessMesh/painlessMesh",
        #     "folder": "PainlessMesh"},
        # {"repo_path":"adafruit/Adafruit-BMP085-Library",
        #     "folder": "Adafruit-BMP085"},
        # {"repo_path":"adafruit/DHT-sensor-library",
        #     "folder": "DHT-sensor"},
        # {"repo_path":"adafruit/Adafruit_Sensor",
        #     "folder": "Adafruit_Sensor"},
        # {"repo_path":"dancol90/ESP8266Ping",
        #     "folder": "ESP8266Ping"},
    ]
})
