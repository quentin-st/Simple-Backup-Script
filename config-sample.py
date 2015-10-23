#!/usr/bin/python3
# -*- coding: utf-8 -*-

BACKUPS = [
    {
        'name': 'my_backup',
        'profile': 'postgresql',

        'database': 'myDb',
        'database_user': ''
    },
    {
        'name': 'my_backup2',
        'profile': 'mysql',

        'database': 'myDb',
        'database_user': '',
        'database_password': ''
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
