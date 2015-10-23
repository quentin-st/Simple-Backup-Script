#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

        'directories': ['/var/www/']
    }
    #, { ... }
]

TARGETS = [
    {
        'host': 'bkup.domain.com',
        'port': 22,
        'user': 'john',
        'dir': '/home/john/backups/'
    }
]
