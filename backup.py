#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import inspect
import argparse
import time
import socket
import pysftp

import plugins
from plugins import *
from config import BACKUPS, TARGETS
from utils import stdio
from utils.stdio import CRESET, CBOLD, LGREEN


# Functions

def get_supported_backup_profiles():
    plugins_list = {}
    for plugin_pkg_name, plugin_pkg in inspect.getmembers(plugins, inspect.ismodule):
        # Get class from this member
        plugins_list[plugin_pkg_name] = plugin_pkg.get_main_class()
    return plugins_list


def send_file(backup, backup_filepath):
    # Send the file to each target
    for target in TARGETS:
        target_dir = target.get('dir')

        print(CBOLD+LGREEN, "\n==> Connecting to {}...".format(target.get('host')), CRESET)

        # YESTERDAY YOU SAID TOMORROW
        # Init SFTP connection
        conn = pysftp.Connection(
            host=target.get('host'),
            username=target.get('user'),
            port=target.get('port', 22)
        )
        conn._transport.set_keepalive(30)

        # Create destination directory if necessary
        try:
            # Try...
            conn.chdir(target_dir)
        except IOError:
            # Create directories
            current_dir = ''
            for dir in target_dir.split('/'):
                current_dir += dir + '/'
                try:
                    conn.chdir(current_dir)
                except:
                    print('Creating missing directory: ' + current_dir)
                    conn.mkdir(current_dir)
                    conn.chdir(current_dir)
                    pass

        # Build destination filename
        dest_file_name = '{hostname}-{timestamp}-{backup_profile}-{backup_name}.{file_extension}'.format(
            hostname=socket.gethostname(),
            timestamp=time.strftime("%Y%m%d-%H%M"),
            backup_profile=backup.get('profile'),
            backup_name=backup.get('name'),
            file_extension=backup.get('file_extension')
        )

        print(CBOLD+LGREEN, "\n==> Starting transfer: {} => {}".format(backup_filepath, dest_file_name), CRESET)

        conn.put(backup_filepath, target_dir+dest_file_name)

        print(CBOLD+LGREEN, "\n==> Transfer finished.", CRESET)

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
    backup_filepath = plugin.create_backup_file(backup)
    backup['file_extension'] = plugin.file_extension

    # Send it to the moon
    send_file(backup, backup_filepath)

    # Delete the file
    stdio.ppexec('rm {}'.format(backup_filepath))

    plugin.clean()

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
        print("\t[{}] {} ({})".format(str(i), project.get('name'), project.get('profile')))

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
