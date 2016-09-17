# Simple-Backup-Script
The purpose of this script is to offer a generic way to backup files or databases or whatever and send those backups to remote hosts.

## Prerequisites
This script relies on the `pysftp` and `requests`  modules:

```bash
sudo pip install pysftp
```

*Sidenote*: Please be aware that since we use Python 3, you have to make sure that `pip` installs the module for **Python 3**.
If your system ships with Python 2 as the default interpreter, `pip install pysftp` will install `pysftp` for **Python 2**.
In that case, you might want to install `pip3` and run :

```bash
sudo pip3 install pysftp
sudo pip3 install requests
```


## How does it work?
There are two customizable steps in this process:

### Backup
This step copies files or dumps databases and puts everything in a single .tar.gz file.
All the logic behind this is contained within a plugin. If you cannot find a suitable plugin (check [`/plugins`](/plugins) dir)
for the content you're trying to save, don't hesitate to create a pull request.

A plugin is quite simple: all it does is to run commands to create the single file, and return its complete file path.
It also contains a `clean` function to delete temporary files created during its execution.

### Transfer
Once everything is ready, let's upload the files to each remote. We can either upload backup files to remote targets, or copy them in a local directory.

#### Remote target configuration
**Note**: *SSH Public Key Authentication* **must** be set up or the script won't connect to your remote backup targets:

1. Generate SSH private (`~/.ssh/id_rsa`) & public (`~/.ssh/id_rsa.pub`) keys if not already done:

    ```bash
    ssh-keygen -t rsa
    ```

2. Copy the public key on the remote server (replace `user` & `123.45.56.78`)

    ```bash
    ssh-copy-id -i ~/.ssh/id_rsa.pub user@123.45.56.78
    ```

    If `~/.ssh/id_rsa.pub` is your default and only ssh key, you can omit the `-i` option and simply use

    ```bash
    ssh-copy-id user@123.45.56.78
    ```

3. Successfully connect without any password

    ```bash
    ssh user@123.45.56.78
    ```

> In both remote and target modes, you have to make sure that the user has the right to write in destination directory.

## Configuration
Copy or rename `config-sample.json` to get `config.json`.

> Note: we switched from `config.py` to `config.json`. Use `backup.py --migrate` to create `config.json`.

### Emails
You can receive an e-mail when a backups fails for whatsoever reason. Just customize the `alert_emails` array
with one or more email addresses. A null, empty array (`[]`) or single empty string array value (`[""]`) will disable
this feature.

```js
"alert_email": ["john@doe.com", "it@doe.com", "accounting@doe.com"],
```

Once done, run the `./backup.py --test-mails` command to check if it works fine.

### Backup profiles
You can add as many backup profiles as you wish.

```js
"my_backup": {              // That's the backup name: no special chars nor spaces please
    "profile": "",          // That's the name of the plugin ("mysql", "filesystem" or whatever)

                            // The whole backup node is sent to the plugin:
    "databases": ["myDb"],  // here are some specific keys
}
```

Check [`config-sample.json`](config-sample.json) for some examples: it contains a sample configuration for each plugin.

### Targets
Each backup profile will then be sent/copied to every target configured. A target can either be `remote` or `local`. Here's a remote sample:

```js
{
    "type":     "remote",
    "host":     "bkup.domain.com",  // Can either be a local/remote IP address
    "port":     22,                 // Optional, default 22
    "user":     "john",
    "dir":      "/home/john/backups/",
    "days_to_keep": 7               // You can override global DAYS_TO_KEEP for each target
}
```

And here's a local sample:

```js
{
    "type":     "local",
    "dir":      "/home/john/backups/",
    "days_to_keep": 7               // You can override global DAYS_TO_KEEP for each target
}
```

For hubiC:

> Note: this target needs `python-swiftclient` package.

> Note2: hubiC dependencies does not support Python 3.2.

```js
{
    "type":             "hubic",
    "dir":              "/Backups/",
    "client_id":        "",
    "client_secret":    "",
    "username":         "",
    "password":         "",
    "container":        "default",
    "days_to_keep":     7           // You can override global DAYS_TO_KEEP for each target
}
```


> **Important note**: the `"dir"` directory must only contain backups from this instance. Any other file could be deleted during backups rotation.

Once done, run the `./backup.py --test-config` command to check if everything's OK.

## Usage
You can either run it in its interactive mode (default), or specify the backup profile you want to run:

```bash
# Interactive mode:
./backup.py

# or
./backup.py --backup my_backup

# or all:
./backup.py --all
```

You can also target a single target by specifying its index in the targets list:

```bash
./backup.py --all --target 0
```

You can configure a daily cron using `crontab -e`: add the following line to the cron file:

```
0 0 * * * /home/user/Simple-Backup-Script/backup.py --all
```

## Plugin-specific considerations
### PostgreSQL
We have to be careful about authorizations. You'll have to create a `.pgpass` file in the cron user's home directory with the
following syntax: `hostname:port:database:username:password`, for example:

```
localhost:5432:db_name:db_user:password
```

In doubt, you can check postgres's port with `sudo netstat -plunt |grep postgres`.

Then, `chmod 600 /home/cron_user/.pgpass`. Running `ls -al /home/cron_user/` must look like this afterwards:

```bash
-rw-------  1 cron_user cron_user   [...] .pgpass
```
