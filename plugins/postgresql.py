import tarfile
import os
import shutil
import tempfile

from utils import stdio


def get_main_class():
    return PostgreSQL


class PostgreSQL():
    key_name = "postgresql"
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
            stdio.ppexec('pg_dump {database} -U {user} -h localhost -f {file_path} --no-password'.format(
                database=database,
                user=backup.get('database_user', database),
                file_path=db_filename
            ))

            tar.add(os.path.basename(os.path.normpath(db_filename)))

        tar.close()

        os.chdir(saved_path)

        return os.path.join(tmp_dir, 'archive.tar.gz')

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
