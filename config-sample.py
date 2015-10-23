#!/usr/bin/python3
# -*- coding: utf-8 -*-

BACKUPS = [
    {
        'name': 'my_backup',
        'profile': 'postgresql',

        'database': 'myDb',
        'database_user': ''
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
