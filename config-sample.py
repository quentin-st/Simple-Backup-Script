#!/usr/bin/python3
# -*- coding: utf-8 -*-

DAYS_TO_KEEP = 15

BACKUPS = [
    {
        'name': 'my_backup',
        'profile': 'postgresql',

        'databases': ['myDb'],
        'database_user': ''
    },
    {
        'name': 'my_backup2',
        'profile': 'mysql',

        'databases': ['myDb1', 'myDb2'],
        'database_user': '',
        'database_password': ''
    },
    {
        'name': 'my_backup3',
        'profile': 'filesystem',

        'directories': [
            '/var/www/*',  # Will compress each subdirectory in a separate .tar.gz
                           # file inside a global .tar.gz file. Use '/var/www/' for single file

            '-/var/www/not-this/'  # Will exclude this directory
        ]
    }
    #, { ... }
]

TARGETS = [
    {
        'type': 'remote',
        'host': 'bkup.domain.com',
        'port': 22,
        'user': 'john',
        'dir': '/home/john/backups/',
        'days_to_keep': 7               # You can override global DAYS_TO_KEEP for each target
    }
]
