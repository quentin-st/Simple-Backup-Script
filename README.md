# Simple-Backup-Script
The purpose of this script is to offer a generic way to backup files or databases or whatever and send those backups to remote hosts.

## Prerequisites
This script relies on the `pysftp` and `requests` modules:

```bash
# Create venv
python3 -m venv ./.venv

# Activate
source .venv/bin/activate

# Install requirements
.venv/bin/pip install -r requirements.txt
```

*Optional*: if you want errors to be reported to Sentry, install its SDK:
```bash
.venv/bin/pip install --upgrade sentry-sdk
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

#### Remote (SFTP) target configuration
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

#### Amazon S3
Simple-Backup-Script supports uploading files to an S3 bucket (either Amazons, or any S3-compatible provider).

1. Install the pip dependency:
    ```bash
    .venv/bin/pip install --upgrade boto3
    ```

2. Configure the credentials ([see boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)):
    ```bash
    mkdir ~/.aws
    vim ~/.aws/credentials
    ```
    ```
    [my-profile-name]
    aws_access_key_id = YOUR_ACCESS_KEY
    aws_secret_access_key = YOUR_SECRET_KEY

    # optional:
    region = eu-west-par
    endpoint_url = https://s3.eu-west-par.io.cloud.ovh.net
    s3 =
      signature_version = s3v4
    request_checksum_calculation = when_required
    response_checksum_validation = when_required
    ```

## Configuration
Copy or rename `config-sample.json` to get `config.json`.

> Note: we switched from `config.py` to `config.json`. Use `backup.py --migrate` to create `config.json`.

### Emails
You can receive an e-mail when a backups fails for whatsoever reason. Just customize the `alert_emails` array
with one or more email addresses. A null, empty array (`[]`) or single empty string array value (`[""]`) will disable
this feature.

```json
"alert_email": ["john@doe.com", "it@doe.com", "accounting@doe.com"],
```

Once done, run the `./backup.py --test-mails` command to check if it works fine.


## Sentry reporting
Errors can be reported to Sentry:

```json
"sentry_dsn": "https://123456789abcdef@o1237.ingest.sentry.io/1234567"
```

### Backup profiles
You can add as many backup profiles as you wish.

```json
"my_backup": {              // That's the backup name: no special chars nor spaces please
    "profile": "",          // That's the name of the plugin ("mysql", "filesystem" or whatever)

                            // The whole backup node is sent to the plugin:
    "databases": ["myDb"],  // here are some specific keys
}
```

Check [`config-sample.json`](config-sample.json) for some examples: it contains a sample configuration for each plugin.

### Targets
Each backup profile will then be sent/copied to every target configured. A target can either be one of the following:

> Note: setting `days_to_keep` to `-1` will disable backups rotation.

> **Important note**: the `"dir"` directory must only contain backups from this instance. Any other file could be deleted during backups rotation.

Once done, run the `./backup.py --test-config` command to check if everything's OK.

#### Remote (SFTP)
```json
{
    "type":     "remote",
    "host":     "bkup.domain.com",  // Can either be a local/remote IP address
    "port":     22,                 // Optional, default 22
    "user":     "john",
    "dir":      "/home/john/backups/",
    "days_to_keep": 7               // You can override global DAYS_TO_KEEP for each target
}
```

#### Local (simple copy)

```json
{
    "type":     "local",
    "dir":      "/home/john/backups/",
    "days_to_keep": 7               // You can override global DAYS_TO_KEEP for each target
}
```

#### FTP
```json
{
    "type":     "ftp",
    "host":     "bkup.domain.com",  // Can either be a local/remote IP address
    "port":     21,                 // Optional, default 21
    "user":     "john",
    "password": "j0hn",
    "dir":      "/home/john/backups/"
}
```

#### S3

```json
{
    "type": "s3",
    "bucket": "my-server-backups",            // Bucket name
    "profile": "my-.aws/credentials-profile"  // Name of the profile in your .aws/credentials file (fallbacks to "default")
}
```

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

You can configure a daily cron using `crontab -e`: add the following line to the cron file.
Tip: use [cronic](https://habilis.net/cronic/) from `moreutils` (`sudo apt install moreutils`) so that cron notifies you
on error, but still include the full script output.

```
0 0 * * * cronic /home/user/Simple-Backup-Script/.venv/bin/python /home/user/Simple-Backup-Script/backup.py --all
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

## Permissions

When building your profiles list, please be aware of permissions issues that may arise.
Your (unprivileged) backups user should be able to access all the files that are referenced in this script's
configuration file.
For database dumps, it's recommended to create a specific user with limited roles (SELECT & LOCK should be fine).

For filesystem archives, you can use ACLs to grant permissions: (replace `USER="backups"` with the name of your Unix user)

```bash
function set_acl() {
    # set ACL on var folder if necessary
    USER="backups"
    FOLDER="$1"
    ACL=$(getfacl "$FOLDER" | grep -E "$USER:..x$" -ic)
    if [[ "$ACL" != 4 ]]; then
        echo "setting missing ACLs on $FOLDER"
        setfacl -R -m u:"$USER":rX "$FOLDER" && setfacl -dR -m u:"$USER":rX "$FOLDER"
    fi
}

set_acl "my/path/to/backup"
```
