# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73

import paramiko
import os

DEFAULT_LOCAL_FILES_DIR = os.getcwd()
REMOTE_DIR_PATH = '/tmp'
UPLOAD_FILE_NAMES = ['upgmgr.mk', 'dcoField.tar.gz.mk']

ssh_client = None

# cmd arguments:
HOSTNAME = "10.100.57.99"


def connect_ssh(hostname: str, username: str = 'root', password: str = '') -> None:
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


def find_local_files_paths(local_files_dir: str = DEFAULT_LOCAL_FILES_DIR,
                           file_names=UPLOAD_FILE_NAMES) -> list:
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
            raise Exception("All files are not available")

    print("Confirmed: Required files are present")
    return files_abs_paths


def create_remote_dir(ftp_client, remote_dir: str):
    try:
        ftp_client.chdir(remote_dir)  # Test if remote dir exists
    except IOError:
        ftp_client.mkdir(remote_dir)  # Create remote dir
        ftp_client.chdir(remote_dir)  # cd to remote dir


def upload_files(list_localfilepaths: list, remotefiledir: str = REMOTE_DIR_PATH):
    # Note: File transfer is handled by the ftp protocol
    ftp_client = ssh_client.open_sftp()
    create_remote_dir(ftp_client, remotefiledir)
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


def exec_cmd(command):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
    except Exception:
        raise Exception(f"Execution failed for: {command}")
    else:
        print(f"Executed successfully: {command}")
    print("Output of the command is following:")
    for line in stdout:
        # print each line in the remote output
        print(line)


# employ ctrl + c to terminate program
# parseargs features
def upgrade_firmware():
    upload_file_paths = find_local_files_paths(local_files_dir=DEFAULT_LOCAL_FILES_DIR)
    connect_ssh(hostname=HOSTNAME)
    upload_files(upload_file_paths)
    close_ssh()


def close_ssh():
    if ssh_client:
        ssh_client.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    upgrade_firmware()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
