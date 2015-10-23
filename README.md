# Simple-Backup-Script
The purpose of this script is to offer a generic way to backup files or databases and send those backups to remote hosts.

## Prerequisites
This script relies on the `pysftp` module:

    sudo pip install pysftp


*Sidenote*: Please be aware that since we use Python 3, you have to make sure that `pip` installs the module for **Python 3**. If your system ships with Python 2 as the default interpreter, `pip install pysftp` will install `pysftp` for **Python 2**.
In that case, you might want to install `pip3` and run :

    sudo pip3 install pysftp

## How does it works?
There are two customizable steps in this process:

### Backup
This step copies the file or dumps the database and put everything in a single file.
All the logic behind this is contained in a plugin. If you cannot find a suitable plugin (check /plugins)
for the content you're trying to save, don't hesitate to create a pull request.

A plugin is quite simple: all it does is to run commands to create the single file, and returns its complete file path.

### Transfer
Once we created the backup file, let's transfer it. See configuration below for more information.

**Note**: *SSH Public Key Authentication* **must** be set up or the script won't connect to your backup targets.

## Configuration
Copy or rename `config-sample.py` to get `config.py`.
Its content looks like this:

    'my_backup': {              # That's the backup name: no special chars nor spaces please
        'profile': '',          # This is the name of the plugin
        
                                # The whole backup node is sent to the plugin:
        'database': 'myDb',     # here are some specific keys
    }

### Plugin-specific considerations
## PostgreSQL
We have to be careful about authorizations. You'll have to create a `.pgpass` file in the cron user's home directory with the
following syntax: `hostname:port:database:username:password`, for example:

    localhost:5432:db_name:db_user:password

In doubt, you can check postgres's port with `sudo netstat -plunt |grep postgres`.

Then, `chmod 600 /home/cron_user/.pgpass`. Running `ls -al /home/cron_user/` must look like this afterwards:

    -rw-------  1 cron_user cron_user   [...] .pgpass

