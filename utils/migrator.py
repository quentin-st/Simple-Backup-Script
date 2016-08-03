import os
import json
from utils.stdio import CBOLD, CRESET, LWARN, LGREEN

config_old_path = 'config.py'
config_new_path = 'config.json'


def migrate():
    # Migrates old config file (config.py) to new one (config.json)
    if not os.path.isfile(config_old_path):
        print(CBOLD+LWARN, 'Could not read {}: no such file'.format(config_old_path), CRESET)
        return False

    # Don't overwrite config.json
    if os.path.isfile(config_new_path):
        print(CBOLD+LWARN, '{} already exists'.format(config_new_path), CRESET)
        return False

    from config import BACKUPS, TARGETS, DAYS_TO_KEEP
    data = {
        'days_to_keep': DAYS_TO_KEEP,
        'backups': BACKUPS,
        'targets': TARGETS
    }

    with open(config_new_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
        print(LGREEN, 'Migrated old configuration to new format.', CRESET)

    return True
