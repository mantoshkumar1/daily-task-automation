# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73

import paramiko
import os
# import requests
import wget
from datetime import datetime
import time

DEFAULT_LOCAL_FILES_DIR = os.getcwd()
REMOTE_DIR_PATH = '/tmp'
UPLOAD_FILE_NAMES = ['upgmgr', 'dcoField.tar.gz']
ssh_client = None
HOSTNAME = "10.100.57.99"
USERNAME = "root"
PASSWORD = ''
PREVIOUS_FW_VERSION='' # todo
UPGRADED_FW_VERSION = '' # todo


class Stage_1_Download_FW_SOFTWARE:
    def __init__(self):
        self.remote_files_path_list = None

    def step_1_get_remote_files(self):
        self.remote_files_path_list = 1

    def step_2_download_firmware(self):
        # test url is fine
        # download
        # what if you have already downloaded files: Show the name of those files to user and
        # ask them if they would like to use the existing files or download? If use existing then expect
        # yes ... if user says : No... then downlaod the file
        print("Example of firmware image URL: https://iartifactory.infinera.com/artifactory/DCO-FW/release/dco-p1-1.92.2/image/")
        # firmware_url = input("Enter the URL of firmware image: ")
        #for f in self.remote_files_path_list:
        #    pass

        print("hello")


class Stage_2_Start_Telnet_Machine:
    def step_1_connect_telnet(self):
        pass
    def step_2_execute_commands(self):
        pass

class Stage_3_Upgrade_FW:
    def __init__(self):
        self.local_files_path_list = None

    def step_1_find_local_files_paths(self, local_files_dir: str = DEFAULT_LOCAL_FILES_DIR,
                               file_names=UPLOAD_FILE_NAMES) -> None:
        # check user input directory is valid or not
        if local_files_dir != DEFAULT_LOCAL_FILES_DIR:
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
                raise Exception(f"str(f_abs_path) is not available")

        print(f"Success: All the required {str(UPLOAD_FILE_NAMES)} files are present")
        self.local_files_path_list = files_abs_paths

    def step_2_connect_ssh(self, hostname: str = HOSTNAME, username: str = USERNAME, password: str = PASSWORD) -> None:
        global ssh_client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=hostname, username=username, password=password)
        except paramiko.AuthenticationException:
            # This exception takes care of Authentication errors & exceptions
            raise Exception('ERROR : Authentication failed because of irrelevant details!')
        except Exception:
            raise Exception(f"Error: Cannot connect to the {hostname}. The board cannot start"
                            f" after reboot, it needs to power cycle from SW host bard")
        print("ssh connection is established")

    def step_3_upload_files(self, list_localfilepaths: list = None, remotefiledir: str = REMOTE_DIR_PATH):
        if not list_localfilepaths:
            list_localfilepaths = self.local_files_path_list
        # Note: File transfer is handled by the ftp protocol
        ftp_client = ssh_client.open_sftp()
        self.mkdir_cd_remote_dir(ftp_client, remotefiledir)
        for l_file_path in list_localfilepaths:
            _, file_name = os.path.split(l_file_path)
            try:
                ftp_client.put(l_file_path, file_name)
            except Exception:
                ftp_client.close()
                raise Exception(f"Upload failed for: {l_file_path}")
            else:
                print(f"Upload successful for: {file_name}")
        ftp_client.close()

    def step_4_execute_upgrade_commands(self):
        self.exec_cmd('ls -lrt')
        self.exec_cmd('/opt/infinera/img/bin/stop_dco')
        self.exec_cmd('cd /tmp')
        self.exec_cmd('./upgmgr -f')

    def step_5_set_firmware_ip_address(self):
        self.exec_cmd("sed -i -r 's/127.8.0.3/0.0.0.0/g' /etc/systemd/system/gnxi.service")
        time.sleep(2)
        self.exec_cmd('systemctl daemon-reload')
        time.sleep(10)
        self.exec_cmd('systemctl restart gnxi')


    def mkdir_cd_remote_dir(self, ftp_client, remote_dir: str) -> None:
        """
        CD to remote directory if remote directory exists, otherwise create one and CD to it
        :param ftp_client:
        :type ftp_client:
        :param remote_dir:
        :type remote_dir:
        :return:
        :rtype:
        """
        try:
            ftp_client.chdir(remote_dir)  # Test if remote dir exists
        except IOError:
            ftp_client.mkdir(remote_dir)  # Create remote dir
            ftp_client.chdir(remote_dir)  # cd to remote dir

    def download_files(self, remote_files_path: list, local_path='.'):
        ftp_client = ssh_client.open_sftp()
        for r in remote_files_path:
            ftp_client.get(r, local_path)
        ftp_client.close()

    def exec_cmd(self, command):
        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
        except Exception:
            raise Exception(f"Execution failed for: {command}")
        else:
            print(f"Executed successfully: {command}")
        print("Output of the command is following:") # todo: there is no output??
        for line in stdout:
            # todo: print each line in the remote output. Verify if it works??
            print(line)

    def close_ssh(self):
        if ssh_client:
            ssh_client.close()



#todo: employ ctrl + c to terminate program
def welcome():
    current_time = datetime.now().strftime("%H:%M:%S")
    hour = int(current_time.split(':')[0])
    if 4 <= hour < 12:
        msg = 'Good Morning'
    elif 12 <= hour < 5:
        msg = 'Good Afternoon'
    elif 5 <= hour < 8:
        msg = 'Good Evening'
    else:
        msg = 'Good Night... Family does not wait for time. Take rest!'
    print(msg)
    print("..............................................................")
    print(f".               Current Time: {current_time} (Canada)             .")
    print(".    Please make sure to have a stable internet connection   .")
    print("..............................................................")
    # fw_ssh_ip_addr = input("Enter Firmware IP address: ")
    # sw_serial_telnet_ip_addr = input("Enter Software serial connection IP address: ")
    # sw_serial_telnet_port = input("Enter Software serial connection Port Number: ")
    input("Press Enter to continue: ")

def bye():
    current_time = datetime.now().strftime("%H:%M:%S")
    print("\n")
    print("..............................................................")
    print(".              Thank you for using this application          .")
    print(f".               Current Time: {current_time} (Canada)             .")
    print("..............................................................")
    print(f"Previous Firmware Version: {PREVIOUS_FW_VERSION}")
    print(f"Upgraded Firmware Version: {UPGRADED_FW_VERSION}")
    print("Dasvidaniya.")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Stage 0: Welcome
    welcome()

    # Stage 1: Download Firmware in local system
    stage_1 = Stage_1_Download_FW_SOFTWARE()
    stage_1.step_1_get_remote_files()
    stage_1.step_2_download_firmware()

    # Stage 2: Start Telnet Machine
    stage_2 = Stage_2_Start_Telnet_Machine()
    stage_2.step_1_connect_telnet()
    stage_2.step_2_execute_commands()

    # Stage 3: Upgrade Firmware and set ip address
    stage_3 = Stage_3_Upgrade_FW()
    stage_3.step_1_find_local_files_paths()
    stage_3.step_2_connect_ssh()
    stage_3.step_3_upload_files()
    stage_3.step_4_execute_upgrade_commands()
    stage_3.step_5_set_firmware_ip_address()
    stage_3.close_ssh()

    # Stage infinity:
    bye()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
