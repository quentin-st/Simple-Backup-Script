#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Easy & simple yet flexible backup script """

import sys
import os
import argparse
import time
import socket
import traceback
import json
import plugins
import targets
from utils.stdio import CRESET, CBOLD, LGREEN, CDIM, LWARN

__author__ = 'Quentin Stoeckel'
__copyright__ = 'Copyright 2016, Quentin Stoeckel and contributors'
__credits__ = ['Contributors at https://github.com/chteuchteu/Simple-Backup-Script/graphs/contributors']

__license__ = 'gpl-v2'
__version__ = '1.0.0'
__maintainer__ = "qstoeckel"
__email__ = 'stoeckel.quentin@gmail.com'
__status__ = 'Production'

config = {
    'days_to_keep': 15,
    'backups': [],
    'targets': []
}
config_filename = 'config.json'
config_filename_old = 'config.py'
config_filepath = os.path.join(os.path.dirname(__file__), config_filename)
config_filepath_old = os.path.join(os.path.dirname(__file__), config_filename_old)


# Functions
def load_config():
    # Load config
    if not os.path.isfile(config_filepath):
        if os.path.isfile(config_filepath_old):
            print(CBOLD + LWARN, '\n{} is deprecated. Please use --migrate to generate {}'.format(
                config_filename_old, config_filename), CRESET)
        else:
            print(CBOLD + LWARN, '\nCould not find configuration file {}'.format(config_filename), CRESET)

        sys.exit(1)

    with open(config_filepath, 'r') as config_file:
        json_config = json.load(config_file)

    config['days_to_keep'] = json_config.get('days_to_keep', config['days_to_keep'])
    config['alert_emails'] = json_config.get('alert_emails')
    config['sentry_dsn'] = json_config.get('sentry_dsn')
    config['backups'] = json_config.get('backups', [])
    config['targets'] = json_config.get('targets', [])

    # Now that we know if Sentry should be enabled, load its sdk:
    init_sentry()


def send_file(backup, backup_filepath, target_profile):
    # Build destination filename
    filename, file_extension = os.path.splitext(backup_filepath)
    # ...explicitly handle ".tar.gz" extensions
    if backup_filepath.endswith('.tar.gz'):
        file_extension = '.tar.gz'

    dest_file_name = 'backup-{hostname}-{timestamp}-{backup_name}({backup_profile}){file_extension}'.format(
        hostname=socket.gethostname(),
        timestamp=time.strftime("%Y%m%d-%H%M"),
        backup_profile=backup.get('profile'),
        backup_name=backup.get('name'),
        file_extension=file_extension
    )

    _targets = targets.get_supported_targets()
    type = target_profile.get('type', 'remote')
    if type not in _targets:
        print("Unknown target type \"{}\".".format(type))
        sys.exit(1)

    target = _targets[type]()
    error = target.copy_to_target(config, target_profile, backup_filepath, dest_file_name)

    if error is not None:
        e, traceback = error
        handle_error(backup, e, traceback)
        print('')


def get_backup(backup_name):
    candidates = [b for b in config['backups'] if b.get('name') == backup_name]
    return candidates[0] if len(candidates) == 1 else None


def do_backup(backup):
    backup_profile = backup.get('profile')

    # Check backup profile
    profiles = plugins.get_supported_backup_profiles()
    if backup_profile not in profiles:
        print("Unknown project type \"{}\".".format(backup_profile), file=sys.stderr)
        sys.exit(1)

    # JUST DO IT
    print(CBOLD+LGREEN, "Creating backup file", CRESET)
    plugin = profiles[backup_profile]()
    backup_filepath = plugin.create_backup_file(backup)
    if backup_filepath is None:
        print("Could not create backup file for \"{}\".".format(backup_profile), file=sys.stderr)
        return

    # Send it to the moon (to each target)
    backup_targets = config['targets'] if args.target == 'all' else [config['targets'][int(args.target)]]
    for target_profile in backup_targets:
        try:
            send_file(backup, backup_filepath, target_profile)
        except Exception as e:
            # Print exception (for output in logs)
            print(traceback.format_exc(), file=sys.stderr)

            handle_error(backup, e, traceback)

    # Delete the file
    if plugin.remove_artifact:
        print(CDIM, "Deleting {}".format(backup_filepath), CRESET)
        os.remove(backup_filepath)
    plugin.clean()

    return


def init_sentry():
    sentry_dsn = config.get('sentry_dsn', None)
    if sentry_dsn is not None:
        try:
            import sentry_sdk
            sentry_sdk.init(sentry_dsn)
            return sentry_sdk
        except Exception as error:
            print(error)

    return None


def handle_error(backup, exception, traceback):
    # sentry
    sentry = init_sentry()
    if sentry is not None:
        sentry.set_level('error')
        sentry.set_tag('backup', backup.get('name'))
        sentry.capture_exception(exception)

    # mails
    email_addresses = config.get('alert_emails', None)
    if email_addresses is not None:
        message = 'Simple-Backup-Script: backup "{}" failed'.format(backup.get('name'))
        formatted_traceback = traceback.format_exc()

        for address in [a for a in email_addresses if a]:
            if address:
                send_mail(address, message, formatted_traceback)


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
    # Check python version
    if sys.version_info.major < 3:
        print('Warning: Python 2.x isn\'t officially supported. Use at your own risk.', file=sys.stderr)

    # Check command line arguments
    parser = argparse.ArgumentParser(description='Easily backup projects')
    parser.add_argument('--self-update', action='store_true', dest='self_update')
    parser.add_argument('--backup', default='ask_for_it')
    parser.add_argument('--target', default='all')
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
            print(CDIM+LWARN, "Cannot self-update: missing .git directory", CRESET, file=sys.stderr)
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
                        print('Could not send mail to {}'.format(address), file=sys.stderr)

            if not mail_sent:
                print('No mail could be sent.', file=sys.stderr)
        else:
            print('"alert_emails" is null or empty.', file=sys.stderr)
            sys.exit(1)

    elif args.test_config:
        print('Opening {}'.format(config_filename))

        try:
            load_config()

            if len(config['backups']) == 0:
                print(LWARN, 'Error: there a no configured backup profile', CRESET, file=sys.stderr)
                sys.exit(1)

            if len(config['targets']) == 0:
                print(LWARN, 'Error: there are no configured targets', CRESET, file=sys.stderr)
                sys.exit(1)

            print(CBOLD + LGREEN, '{} successfully parsed:'.format(config_filename), CRESET)
            print('  - Default days_to_keep: {}'.format(config['days_to_keep']))
            print('  - Alert emails: {}'.format(config['alert_emails']))
            print('  - {} backup profile(s)'.format(len(config['backups'])))
            print('  - {} backup target(s)'.format(len(config['targets'])))

            for i, target in enumerate(config['targets']):
                if target.get('host') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "host" attribute in target {}'.format(i), CRESET, file=sys.stderr)
                host = target.get('host', '#{}'.format(i+1))
                if target.get('user') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "user" attribute in target {}'.format(host), CRESET, file=sys.stderr)
                if target.get('dir') is None:
                    print(CBOLD + LWARN, 'Warning: Missing "dir" attribute in target {}'.format(host), CRESET, file=sys.stderr)

        except Exception:
            print('Could not parse configuration:', file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)

    else:
        load_config()

        # Ask for backup to run
        if len(config['backups']) == 0:
            print(CBOLD + LGREEN, "Please configure backup projects in backup.py", CRESET, file=sys.stderr)
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
                print("This backup does not exist, or there may be several backups with this name", file=sys.stderr)
                sys.exit(1)
            else:
                do_backup(backup)
except KeyboardInterrupt:
    print('\n^C signal caught, exiting')
    sys.exit(1)
