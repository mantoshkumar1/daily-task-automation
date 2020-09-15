from logics.app_constants import *
import os

APP_CFG = {
    HOSTNAME: "10.100.57.99",
    USERNAME: 'root',
    PASSWORD: '',
    DEFAULT_LOCAL_FILES_DIR: os.path.join(os.getcwd(), 'files_container'),
    REMOTE_DIR_PATH: '/tmp',
    UPLOAD_FILE_NAMES: ['upgmgr', 'dcoField.tar.gz'],
    LOG_LOC: os.path.join(os.getcwd(), 'logs') # todo??  incomplete
}
