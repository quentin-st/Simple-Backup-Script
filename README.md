# Simple-Backup-Script
The purpose of this script is to offer a generic way to backup files or databases and send those backups to remote hosts.

## How does it works?
There are two customizable steps in this process:

### Backup
This step copies the file or dumps the database and put everything in a .tar.gz file.
All the logic behind this is contained in a plugin. If you cannot find a suitable plugin (check /plugins)
for the content you're trying to save, don't hesitate to create a pull request.

A plugin is quite simple: all it does is to run commands to create the .tar.gz file, and returns its complete file path.

### Transfer
Once we created the backup file, let's transfer it. See configuration below for more information.

**Note**: *SSH Public Key Authentication* **must** be set up or the script won't connect to your backup targets.

## Configuration
Copy or rename `config-sample.py` to get `config.py`.
Its content looks like this:

    'my_backup': {              # That's the backup name: no special chars nor spaces please
        'profile': '',          # This is the name of the plugin
        
        'host': 'localhost',    # The whole backup node is sent to the plugin:
        'database': 'myDb',     # here are some specific keys
        
        'target': {             # This allows to sftp the backup file to the remote host
            'host': 'bkup.domain.com',
            'user': 'john',
            'dir': '/home/john/backups/'
        }
    }

