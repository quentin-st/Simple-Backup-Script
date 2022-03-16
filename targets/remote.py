import os
import datetime
import traceback

from utils.stdio import CDIM, CRESET, CBOLD, LGREEN, print_progress


def get_main_class():
    return Remote


class Remote:
    def copy_to_target(self, config, target, local_filepath, target_filename):
        import pysftp

        user = target.get('user')
        host = target.get('host')
        port = target.get('port', 22)
        password = target.get('password')

        print('')
        print(CBOLD + LGREEN, "Connecting to {}@{}:{}...".format(user, host, port), CRESET)

        # Init SFTP connection
        try:
            cnopts = pysftp.CnOpts()
            if target.get('disable_hostkey_checking', False):
                cnopts.hostkeys = None

            conn = pysftp.Connection(
                host=host,
                username=target.get('user'),
                port=port,
                password=password,
                cnopts=cnopts
            )

            conn._transport.set_keepalive(30)
        except (pysftp.ConnectionException, pysftp.SSHException) as e:
            print(CBOLD, "Unknown exception while connecting to host:", CRESET)
            print(traceback.format_exc())
            return e, traceback
        except (pysftp.CredentialException, pysftp.AuthenticationException) as e:
            print(CBOLD, "Credentials or authentication exception while connecting to host:", CRESET)
            print(traceback.format_exc())
            return e, traceback

        target_dir = target.get('dir')

        # Create destination directory if necessary
        try:
            # Try...
            conn.chdir(target_dir)
        except IOError:
            # Create directories
            current_dir = ''
            for directory in target_dir.split('/'):
                current_dir = os.path.join(current_dir, directory)
                try:
                    conn.chdir(current_dir)
                except IOError:
                    print(CDIM, 'Creating missing directory {}'.format(current_dir), CRESET)
                    conn.mkdir(current_dir)
                    conn.chdir(current_dir)
                    pass

        print(CBOLD + LGREEN, "Starting transfer: {} => {}".format(local_filepath, target_filename), CRESET)

        # Upload file
        conn.put(local_filepath, target_filename, callback=print_progress)

        print('')
        print(CBOLD + LGREEN, "Transfer finished.", CRESET)

        self.rotate_backups(config, target, conn)

        conn.close()

    def rotate_backups(self, config, target, conn):
        backup_dir = target.get('dir')
        days_to_keep = target.get('days_to_keep', config['days_to_keep'])

        if days_to_keep == -1:
            return

        # CD to backups dir
        conn.chdir(backup_dir)

        now = datetime.datetime.now()
        # Loop over all files in the directory
        for file in conn.listdir(backup_dir):
            if file.startswith('backup-'):
                fullpath = os.path.join(backup_dir, file)

                if conn.isfile(fullpath):
                    timestamp = conn.stat(fullpath).st_atime
                    createtime = datetime.datetime.fromtimestamp(timestamp)
                    delta = now - createtime

                    if delta.days > days_to_keep:
                        print(CBOLD + LGREEN, "Deleting backup file {file} ({days} days old)".format(
                            file=file, days=delta
                        ), CRESET)
                        conn.unlink(file)
