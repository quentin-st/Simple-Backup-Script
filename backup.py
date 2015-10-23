#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import inspect
import plugins
from plugins import *
from config import BACKUPS
from utils import stdio
from utils.stdio import CRESET, CBOLD, LGREEN


# Functions

def get_supported_backup_profiles():
    """Registers the supported project types"""
    plugins_list = {}
    for plugin_pkg_name, plugin_pkg in inspect.getmembers(plugins, inspect.ismodule):
        plugin_variants = plugin_pkg.register_variants()
        for plugin_variant in plugin_variants:
            plugins_list[plugin_variant.key_name] = plugin_variant
    return plugins_list


def send_file(backup, backup_filepath):
    # Get connection information
    target = backup.get('target')
    host = target.get('host')
    port = target.get('port', 22)
    user = target.get('user')
    dir = target.get('dir')

    # Build remote filepath
    remote_path = dir + backup_filepath  # TODO

    print(CBOLD+LGREEN, "\n==> Starting transfer from {} to {}".format(backup_filepath, remote_path), CRESET)

    # YESTERDAY YOU SAID TOMORROW
    stdio.ppexec('scp -P {port} {user}@{host}:{remote_path} {local_path}'.format(
        user=user,
        host=host,
        port=port,
        remote_path=remote_path,
        local_path=backup_filepath
    ))

    print(CBOLD+LGREEN, "\n==> Transfer finished.".format(backup_filepath, remote_path), CRESET)

    return


def do_backup(backup_name):
    # Get infos from conf
    if backup_name not in BACKUPS.keys():
        print("Unknown project \"{}\".".format(backup_name))
        sys.exit(1)

    backup = BACKUPS.get(backup_name)
    backup_profile = backup.get('profile')

    # Check backup profile
    profiles = get_supported_backup_profiles()
    if backup_profile not in profiles:
        print("Unknown project type \"{}\".".format(backup_profile))
        sys.exit(1)

    # JUST DO IT
    print(CBOLD+LGREEN, "\n==> Creating backup file", CRESET)
    plugin = profiles[backup_profile]()
    backup_filepath = getattr(plugin, 'create_backup_file')()

    # Send it to the moon
    send_file(backup, backup_filepath)

    return

