import threading

import os
import paramiko

from default_cfg import APP_CFG as dflt_cfg
from .app_constants import *


class Session:
    """
    Implements the logics for:
    1. ssh and ftp connection establishment and termination
    2. File upload using ftp protocol
    """
    __singleton_lock = threading.Lock()

    # this will hold the instance of session instance
    __session_instance = None

    def __init__(self):
        self._ssh_client = None
        self._ftp_client = None

    def start_session(self):
        """Establish the ssh and ftp connection"""
        self._ssh_client = Session.__establish_ssh_connection()
        self._ftp_client = self._ssh_client.open_sftp()

    def close_session(self):
        """Closes established ssh and ftp connection"""
        if self._ssh_client:
            self._ssh_client.close()
        if self._ftp_client:
            self._ftp_client.close()

    @classmethod
    def __establish_ssh_connection(
            cls,
            hostname: str = dflt_cfg[HOSTNAME],
            username: str = dflt_cfg[USERNAME],
            password: str = dflt_cfg[PASSWORD]
    ):
        """
        Establish ssh connect to host with username and password
        :param hostname: IP address or URL
        :type hostname: str
        :param username: user name
        :type username: str
        :param password:
        :type password: str
        :return: instance of ssh-client??
        :rtype: ??
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=hostname, username=username, password=password)
        except paramiko.AuthenticationException:
            # This exception takes care of Authentication errors & exceptions
            raise Exception(
                'ERROR : Authentication failed because of irrelevant details!')
        except Exception:
            raise Exception(
                f"Error: Cannot connect to the {hostname}. The board cannot start"
                f" after reboot, it needs to power cycle from SW host bard")
        print("ssh connection is established")
        return ssh_client

    def mkdir_cd_remote_dir(self, remote_dir: str = dflt_cfg[REMOTE_DIR_PATH]) -> None:
        """
        CD to remote directory if remote directory exists, otherwise create one and
        CD to it
        :param remote_dir:
        :type remote_dir: str
        :return:
        :rtype:
        """
        try:
            self._ftp_client.chdir(remote_dir)  # Test if remote dir exists
        except IOError:
            self._ftp_client.mkdir(remote_dir)  # Create remote dir
            self._ftp_client.chdir(remote_dir)  # cd to remote dir

    def exec_cmd(self, command: str = 'ls -lrt'):
        """
        todo: later
        :param command:
        :type command: str
        """
        try:
            stdin, stdout, stderr = self._ssh_client.exec_command(command)
        except Exception:
            raise Exception(f"Execution failed for: {command}")
        else:
            print(f"Executed successfully: {command}")
        print("Output of the command is following:")
        for line in stdout:
            # print each line of the remote output in the local terminal
            print(line)

    def upload_files(
            self,
            list_local_file_paths: list,
            remote_file_dir: str = dflt_cfg[REMOTE_DIR_PATH]
    ):
        """
        File transfer is handled by the ftp protocol
        :param list_local_file_paths: list of absolute file paths
        :type list_local_file_paths: list
        :param remote_file_dir: remote directory
        :type remote_file_dir: str
        :return:
        :rtype:
        """
        self.mkdir_cd_remote_dir(remote_file_dir)
        for local_file_path in list_local_file_paths:
            _, file_name = os.path.split(local_file_path)
            try:
                print(f"Uploading in progress for file: {file_name}........ Please wait!")
                self._ftp_client.put(local_file_path, file_name)
            except Exception:
                self.close_session()
                raise Exception(f"Upload failed for: {local_file_path}")
            else:
                print(f"Upload successful for: {file_name}")

    @classmethod
    def get_session_instance(cls):
        """
        This function uses “Double Checked Locking” to return an instance of Session
        class. Once a Session object is created then synchronization among threads is no
        longer useful because now obj will not be null and any sequence of operations will
        lead to consistent results. So we will only acquire lock on the
        get_session_instance() once, when the obj is null. This way we only synchronize
        the first way through, just what we want.
        :return: an instance of Session
        """
        if not cls.__session_instance:
            with cls.__singleton_lock:
                if not cls.__session_instance:
                    cls.__session_instance = cls()

        return cls.__session_instance
