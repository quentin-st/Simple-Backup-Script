import tarfile
import os
import shutil
import tempfile

from utils import stdio


def get_main_class():
    return MySQL


class MySQL:
    key_name = "mysql"
    remove_artifact = True

    def __init__(self):
        self.temp_dir = ''

    def create_backup_file(self, backup):
        # Create temporary working directory
        tmp_dir = tempfile.mkdtemp()
        self.temp_dir = tmp_dir

        # Create tar file
        saved_path = os.getcwd()
        os.chdir(tmp_dir)

        tar = tarfile.open('archive.tar.gz', 'w:gz')

        # Loop over databases
        for database in backup.get('databases'):
            db_filename = database + '.sql'

            # Dump db
            stdio.ppexec('mysqldump -u {user} -p\'{password}\' --no-tablespaces {database} > {file_path}'.format(
                user=backup.get('database_user'),
                password=backup.get('database_password').replace("'", "\\'"),
                database=database,
                file_path=db_filename
            ))

            tar.add(os.path.basename(os.path.normpath(db_filename)))

        tar.close()

        os.chdir(saved_path)

        return os.path.join(tmp_dir, 'archive.tar.gz')

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
