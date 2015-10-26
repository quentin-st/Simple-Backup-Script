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
It also contains a `clean` function to delete temporary files created during its execution.

### Transfer
Once we created the backup file, let's transfer it. See configuration below for more information.

**Note**: *SSH Public Key Authentication* **must** be set up or the script won't connect to your backup targets:

1. Generate SSH private (`~/.ssh/id_rsa`) & public (`~/.ssh/id_rsa.pub`) keys if not already done:
    
        ssh-keygen -t rsa
    
2. Copy the public key on the remote server (replace `user` & `123.45.56.78`)

        cat ~/.ssh/id_rsa.pub | ssh user@123.45.56.78 "mkdir -p ~/.ssh && cat >>  ~/.ssh/authorized_keys"

3. Successfully connect without any password

        ssh user@123.45.56.78


## Configuration
Copy or rename `config-sample.py` to get `config.py`.

### Backup profiles
You can add as many backup profiles as you wish.

    'my_backup': {              # That's the backup name: no special chars nor spaces please
        'profile': '',          # This is the name of the plugin
        
                                # The whole backup node is sent to the plugin:
        'databases': ['myDb'],  # here are some specific keys
    }

Check the `config-sample.py` for some information: it contains a sample configuration for each plugin.

### Targets
Each backup profile will then be sent to every target configured. Here's a sample:

    {
        'host': 'bkup.domain.com',  # Can either be a local/remote IP address
        'port': 22,                 # Optional, default 22
        'user': 'john',
        'dir': '/home/john/backups/',
        'days_to_keep': 7           # You can override global DAYS_TO_KEEP for each target
    }

**Important note**: the dir must only contain backups from this instance. Any other file could be deleted during backups rotation.

## Usage
You can either run it in its interactive mode (default), or specify the backup you want to achieve:

    # Interactive mode:
    ./backup.py
    
    # or
    ./backup.py --backup my_backup
    
    # or all:
    ./backup.py --all

You can configure a daily cron using `crontab -e`: add the following line to the cron file:

    0 3 * * * /home/user/Simple-Backup-Script/backup.py --all

### Plugin-specific considerations
## PostgreSQL
We have to be careful about authorizations. You'll have to create a `.pgpass` file in the cron user's home directory with the
following syntax: `hostname:port:database:username:password`, for example:

    localhost:5432:db_name:db_user:password

In doubt, you can check postgres's port with `sudo netstat -plunt |grep postgres`.

Then, `chmod 600 /home/cron_user/.pgpass`. Running `ls -al /home/cron_user/` must look like this afterwards:

    -rw-------  1 cron_user cron_user   [...] .pgpass

