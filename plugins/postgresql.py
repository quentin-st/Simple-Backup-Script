import tarfile
import os

from utils import stdio


def get_main_class():
    return PostgreSQL


class PostgreSQL:
    key_name = "postgresql"
    file_extension = "tar.gz"

    def create_backup_file(self, backup):
        # Create temporary working directory
        tmp_dir = stdio.simple_exec('mktemp', '--directory')

        # Create tar file
        saved_path = os.getcwd()
        os.chdir(tmp_dir)

        tar = tarfile.open('archive.tar.gz', 'w:gz')

        # Loop over databases
        for database in backup.get('databases'):
            db_filepath = database + '.sql'

            # Dump db
            stdio.ppexec('pg_dump {database} -U {user} -h localhost -f {file_path} --no-password'.format(
                database=database,
                user=backup.get('database_user', database),
                file_path=db_filepath
            ))

            tar.add(db_filepath)

        tar.close()

        os.chdir(saved_path)

        return tmp_dir + '/archive.tar.gz'
