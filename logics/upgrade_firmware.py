"""Reference: https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73
"""

import os
from default_cfg import APP_CFG as dflt_cfg
from .app_constants import *
from logics.sessions import Session

# todo: cmd arguments 1:
# HOSTNAME = "10.100.57.99"
# todo: cmd arguments 2:
# local files path directory

# todo: give the remote download path of firmware which then downloads the files in files_container.
# also, replace the existing files if files_container has any with the same name.

# todo: verify the input of user coming through argsparse

# todo: add feature to keep files in files_container first. Once thats done, use parseargs to work on any local dir as per user's convenience.
# todo: release a package.


class UpgradeFirmware:
    """
    todo: write later
    """
    def __init__(self):
        self._session = Session.get_session_instance()

    @classmethod
    def find_local_files_abs_paths(
            cls,
            local_files_dir: str = dflt_cfg[DEFAULT_LOCAL_FILES_DIR],
            file_names: list = dflt_cfg[UPLOAD_FILE_NAMES]
    ) -> list:
        """
        Find the absolute file paths of the files that needs to be uploaded
        :param local_files_dir: absolute directory path where uploading files are present
        :type local_files_dir: str
        :param file_names: Name of the files
        :type file_names: list
        :return: absolute file path of the uploading files
        :rtype: list
        """
        # check user input directory is valid or not
        if local_files_dir != dflt_cfg[DEFAULT_LOCAL_FILES_DIR]:
            if not os.path.isdir(local_files_dir):
                raise Exception("Directory of files does not exist")

        # construct absolute addresses of these files
        files_abs_paths = []
        for f_name in file_names:
            f_abs_path = os.path.join(local_files_dir, f_name)
            files_abs_paths.append(f_abs_path)

        # check if all the files exist or not
        for f_abs_path in files_abs_paths:
            if not os.path.isfile(f_abs_path):
                raise Exception(f"{str(f_abs_path)} is not available")

        print(f"Success: All the required files {file_names} are present")
        return files_abs_paths

    # todo: employ ctrl + c to terminate program
    # todo: parseargs features
    def upgrade_firmware(self, remote_file_dir: str = dflt_cfg[REMOTE_DIR_PATH]):
        """
        todo: later
        :param remote_file_dir:
        :type remote_file_dir:
        :return:
        :rtype:
        """
        upload_file_paths = self.find_local_files_abs_paths(
            local_files_dir=dflt_cfg[DEFAULT_LOCAL_FILES_DIR])
        self._session.start_session()
        self._session.upload_files(upload_file_paths, remote_file_dir)
        self._session.exec_cmd()
        self._session.close_session()
