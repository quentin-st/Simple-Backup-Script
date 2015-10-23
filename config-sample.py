#!/usr/bin/python3
# -*- coding: utf-8 -*-

BACKUPS = {
    'my_backup': {
        'profile': 'postgresql',
        'host': 'localhost',
        'database': 'myDb',
        'target': {
            'host': 'bkup.domain.com',
            'user': 'john',
            'dir': '/home/john/backups/'
        }
    }
    #,
    # 'my_other_backup { ... }
}
