# Simple-Backup-Script
The purpose of this script is to offer a generic way to backup files or databases and send those backups to remote hosts.

## Prerequisites
This script relies on the `pysftp` module:

    sudo pip install pysftp

## How does it works?
There are two customizable steps in this process:

### Backup
This step copies the file or dumps the database and put everything in a single file.
All the logic behind this is contained in a plugin. If you cannot find a suitable plugin (check /plugins)
for the content you're trying to save, don't hesitate to create a pull request.

A plugin is quite simple: all it does is to run commands to create the single file, and returns its complete file path.

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

