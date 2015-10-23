#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import inspect
import argparse
import time
import socket

import plugins
from plugins import *
from config import BACKUPS
from utils import stdio
from utils.stdio import CRESET, CBOLD, LGREEN


# Functions

def get_supported_backup_profiles():
    plugins_list = {}
    for plugin_pkg_name, plugin_pkg in inspect.getmembers(plugins, inspect.ismodule):
        plugins_list[plugin_pkg_name] = plugin_pkg
    return plugins_list


def send_file(backup, backup_filepath):
    target = backup.get('target')

    # Build remote filepath
    remote_path = '{dir}{hostname}-{timestamp}-{backup_name}.{file_extension}'.format(
        dir=target.get('dir'),
        hostname=socket.gethostname(),
        timestamp=time.strftime("%Y%m%d-%H%M"),
        backup_name=backup.get('name'),
        file_extension=backup.get('file_extension')
    )

    print(CBOLD+LGREEN, "\n==> Starting transfer for {} from {} to {}".format(backup.get('name'), backup_filepath, remote_path), CRESET)

    # YESTERDAY YOU SAID TOMORROW
    stdio.ppexec('scp -P {port} {user}@{host}:{remote_path} {local_path}'.format(
        user=target.get('user'),
        host=target.get('host'),
        port=target.get('port', 22),
        remote_path=remote_path,
        local_path=backup_filepath
    ))

    print(CBOLD+LGREEN, "\n==> Transfer finished.".format(backup_filepath, remote_path), CRESET)

    return


def get_backup(backup_name):
    candidates = [b for b in BACKUPS if b.get('name') == backup_name]
    return candidates[0] if len(candidates) == 1 else None


def do_backup(backup):
    backup_profile = backup.get('profile')

    # Check backup profile
    profiles = get_supported_backup_profiles()
    if backup_profile not in profiles:
        print("Unknown project type \"{}\".".format(backup_profile))
        sys.exit(1)

    # JUST DO IT
    print(CBOLD+LGREEN, "\n==> Creating backup file", CRESET)
    plugin = profiles[backup_profile]()
    backup_filepath = getattr(plugin, 'create_backup_file')(backup)
    backup.set('file_extension', getattr(plugin, 'file_extension'))

    # Send it to the moon
    send_file(backup, backup_filepath)

    # Delete the file
    stdio.ppexec('rm {file_path}'.format(backup_filepath))

    return


# Ask for backup to run
if len(BACKUPS) == 0:
    print(CBOLD+LGREEN, "\nPlease configure backup projects in backup.py", CRESET)
    sys.exit(1)

# Check command line arguments
parser = argparse.ArgumentParser(description='Easily backup projects')
parser.add_argument('--backup', default='ask_for_it')
args = parser.parse_args()

if args.backup == 'ask_for_it':
    print("Please select a backup profile to execute")
    for i, project in enumerate(BACKUPS):
        print("\t[{}] {}".format(str(i), project.get('name')))

    backup_index = -1
    is_valid = 0
    while not is_valid:
        try:
            backup_index = int(input("? "))
            is_valid = 1
        except ValueError:
            print("Not a valid integer.")

    if 0 <= backup_index < len(BACKUPS):
        # Here goes the thing
        backup = BACKUPS[backup_index]

        do_backup(backup)
    else:
        print("I won't take that as an answer")

else:  # Deploy project passed as argument
    backup = get_backup(args.backup)

    if backup is None:
        print("This backup does not exists, or there may be several backups with this name")
        sys.exit(1)
    else:
        do_backup(backup)
