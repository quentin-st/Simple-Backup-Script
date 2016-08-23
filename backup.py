#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import shutil
import sys
import inspect
import argparse
import time
import socket
import datetime
import pysftp
import traceback
import json

import plugins
from plugins import *
from utils.stdio import CRESET, CBOLD, LGREEN, CDIM, LWARN

config = {
    'days_to_keep': 15,
    'backups': [],
    'targets': []
}
config_filename = 'config.json'
config_filename_old = 'config.py'


# Functions
def load_config():
    # Load config
    if not os.path.isfile(config_filename):
        if os.path.isfile(config_filename_old):
            print(CBOLD + LWARN, '\n{} is deprecated. Please use --migrate to generate {}'.format(
                config_filename_old, config_filename), CRESET)
        else:
            print(CBOLD + LWARN, '\nCould not find configuration file {}'.format(config_filename), CRESET)

        sys.exit(1)

    with open(config_filename, 'r') as config_file:
        json_config = json.load(config_file)

    config['days_to_keep'] = json_config.get('days_to_keep', config['days_to_keep'])
    config['alert_emails'] = json_config.get('alert_emails')
    config['backups'] = json_config.get('backups', [])
    config['targets'] = json_config.get('targets', [])


def get_supported_backup_profiles():
    plugins_list = {}
    for plugin_pkg_name, plugin_pkg in inspect.getmembers(plugins, inspect.ismodule):
        # Get class from this member
        plugins_list[plugin_pkg_name] = plugin_pkg.get_main_class()
    return plugins_list


def print_upload_progress(transferred, total):
    workdone = transferred/total
    print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(workdone * 50), workdone * 100), end="", flush=True)


def send_file(backup, backup_filepath):
    # Send the file to each target
    for target in config['targets']:
        type = target.get('type', 'remote')

        # Build destination filename
        dest_file_name = 'backup-{hostname}-{timestamp}-{backup_name}({backup_profile}).{file_extension}'.format(
            hostname=socket.gethostname(),
            timestamp=time.strftime("%Y%m%d-%H%M"),
            backup_profile=backup.get('profile'),
            backup_name=backup.get('name'),
            file_extension=backup.get('file_extension')
        )

        target_dir = target.get('dir')

        if type == 'remote':
            user = target.get('user')
            host = target.get('host')
            port = target.get('port', 22)

            print(CBOLD+LGREEN, "\n==> Connecting to {}@{}:{}...".format(user, host, port), CRESET)

            # Init SFTP connection
            try:
                cnopts = pysftp.CnOpts()
                if target.get('disable_hostkey_checking', False):
                    cnopts.hostkeys = None

                conn = pysftp.Connection(
                    host=host,
                    username=target.get('user'),
                    port=port,
                    cnopts=cnopts
                )

                conn._transport.set_keepalive(30)
            except (pysftp.ConnectionException, pysftp.SSHException):
                print(CBOLD, "Unknown exception while connecting to host:", CRESET)
                print(traceback.format_exc())
                send_mail_on_error(backup, traceback)
                continue
            except (pysftp.CredentialException, pysftp.AuthenticationException):
                print(CBOLD, "Credentials or authentication exception while connecting to host:", CRESET)
                print(traceback.format_exc())
                send_mail_on_error(backup, traceback)
                continue

            # Create destination directory if necessary
            try:
                # Try...
                conn.chdir(target_dir)
            except IOError:
                # Create directories
                current_dir = ''
                for directory in target_dir.split('/'):
                    current_dir = os.path.join(current_dir, directory)
                    try:
                        conn.chdir(current_dir)
                    except:
                        print('Creating missing directory {}'.format(current_dir))
                        conn.mkdir(current_dir)
                        conn.chdir(current_dir)
                        pass

            print(CBOLD+LGREEN, "\n==> Starting transfer: {} => {}".format(backup_filepath, dest_file_name), CRESET)

            # Upload file
            conn.put(backup_filepath, os.path.join(target_dir, dest_file_name), callback=print_upload_progress)

            print(CBOLD+LGREEN, "\n==> Transfer finished.", CRESET)

            rotate_backups(target, conn)

            conn.close()
        elif type == 'local':
            print(CBOLD + LGREEN, "\n==> Starting copy: {} => {}".format(backup_filepath, dest_file_name), CRESET)

            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            shutil.copy(backup_filepath, os.path.join(target_dir, dest_file_name))
    return


def get_backup(backup_name):
    candidates = [b for b in config['backups'] if b.get('name') == backup_name]
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
    try:
        send_file(backup, backup_filepath)
    except Exception:
        # Print exception (for output in logs)
        print(traceback.format_exc())

        send_mail_on_error(backup, traceback)
    finally:
        # Delete the file
        print(CDIM, "Deleting {}".format(backup_filepath), CRESET)
        os.remove(backup_filepath)

        plugin.clean()

    return


def rotate_backups(target, conn):
    backup_dir = target.get('dir')
    # CD to backups dir
    conn.chdir(backup_dir)

    now = datetime.datetime.now()
    # Loop over all files in the directory
    for file in conn.listdir(backup_dir):
        if file.startswith('backup-'):
            fullpath = os.path.join(backup_dir, file)

            if conn.isfile(fullpath):
                timestamp = conn.stat(fullpath).st_atime
                createtime = datetime.datetime.fromtimestamp(timestamp)
                delta = now - createtime

                if delta.days > target.get('days_to_keep', config['days_to_keep']):
                    print(CBOLD+LGREEN, "\n==> Deleting backup file {file} ({days} days old)".format(
                        file=file, days=delta
                    ), CRESET)
                    conn.unlink(file)

    return


def send_mail_on_error(backup, traceback):
    email_addresses = config.get('alert_emails', None)
    if email_addresses is not None:
        for address in [a for a in email_addresses if a]:
            if address:
                send_mail(
                    address,
                    'Simple-Backup-Script: backup "{}" failed'.format(backup.get('name')),
                    traceback.format_exc()
                )


# Inspired by http://stackoverflow.com/a/27874213/1474079
def send_mail(recipient, subject, body):
    import subprocess

    try:
        process = subprocess.Popen(['mail', '-s', subject, recipient], stdin=subprocess.PIPE)
        process.communicate(input=bytes(body, 'UTF-8'))
        return True
    except Exception as error:
        print(error)
        return False


try:
    # Check command line arguments
    parser = argparse.ArgumentParser(description='Easily backup projects')
    parser.add_argument('--self-update', action='store_true', dest='self_update')
    parser.add_argument('--backup', default='ask_for_it')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('--migrate', action='store_true')
    parser.add_argument('--test-mails', action='store_true', dest='test_mails')
    parser.add_argument('--test-config', action='store_true', dest='test_config')
    args = parser.parse_args()

    if args.migrate:
        from utils.migrator import migrate
        migrate()

    elif args.self_update:
        # cd to own directory
        self_dir = os.path.dirname(os.path.realpath(__file__))

        if not os.path.isdir(os.path.join(self_dir, '.git')):
            print(CDIM+LWARN, "Cannot self-update: missing .git directory", CRESET)
            sys.exit(1)

        os.chdir(self_dir)
        os.system("git pull")

        print()
        print(LGREEN, "Updated to the latest version", CRESET)

    elif args.test_mails:
        load_config()

        email_addresses = config['alert_emails']
        mail_sent = False
        if email_addresses:
            for address in [a for a in email_addresses if a]:
                if address:
                    if send_mail(address, 'Simple-Backup-Script: test e-mail', ''):
                        mail_sent = True
                        print('Test mail sent to {}'.format(address))
                    else:
                        print('Could not send mail to {}'.format(address))

            if not mail_sent:
                print('No mail could be sent.')
        else:
            print('"alert_emails" is null or empty.')
            sys.exit(1)

    elif args.test_config:
        print('Opening {}'.format(config_filename))

        try:
            load_config()

            if len(config['backups']) == 0:
                print(LWARN, 'Error: there a no configured backup profile', CRESET)
                sys.exit(1)

            if len(config['targets']) == 0:
                print(LWARN, 'Error: there are no configured targets', CRESET)
                sys.exit(1)

            print(CBOLD + LGREEN, '{} successfully parsed:'.format(config_filename), CRESET)
            print('  - Default days_to_keep: {}'.format(config['days_to_keep']))
            print('  - Alert emails: {}'.format(config['alert_emails']))
            print('  - {} backup profile(s)'.format(len(config['backups'])))
            print('  - {} backup target(s)'.format(len(config['targets'])))

            for i, target in enumerate(config['targets']):
                if target.get('host') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "host" attribute in target #{}'.format(
                        target.get('host', '#{}'.format(i+1))), CRESET)
                if target.get('user') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "user" attribute in target {}'.format(
                        target.get('host', '#{}'.format(i+1))), CRESET)
                if target.get('dir') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "dir" attribute in target {}'.format(
                        target.get('host', '#{}'.format(i+1))), CRESET)

        except Exception:
            print('Could not parse configuration:')
            print(traceback.format_exc())

    else:
        load_config()

        # Ask for backup to run
        if len(config['backups']) == 0:
            print(CBOLD + LGREEN, "\nPlease configure backup projects in backup.py", CRESET)
            sys.exit(1)

        if args.all:
            # Backup all profiles
            for i, project in enumerate(config['backups']):
                print(CBOLD+LGREEN, "\n{} - Backing up {} ({})".format(i, project.get('name'), project.get('profile')), CRESET)

                backup = config['backups'][i]
                do_backup(backup)

        elif args.backup == 'ask_for_it':
            print("Please select a backup profile to execute")
            for i, project in enumerate(config['backups']):
                print("\t[{}] {} ({})".format(str(i), project.get('name'), project.get('profile')))

            backup_index = -1
            is_valid = 0
            while not is_valid:
                try:
                    backup_index = int(input("? "))
                    is_valid = 1
                except ValueError:
                    print("Not a valid integer.")

            if 0 <= backup_index < len(config['backups']):
                # Here goes the thing
                backup = config['backups'][backup_index]

                do_backup(backup)
            else:
                print("I won't take that as an answer")

        else:  # Backup project passed as argument
            backup = get_backup(args.backup)

            if backup is None:
                print("This backup does not exist, or there may be several backups with this name")
                sys.exit(1)
            else:
                do_backup(backup)
except KeyboardInterrupt:
    print('\n^C signal caught, exiting')
    sys.exit(1)
