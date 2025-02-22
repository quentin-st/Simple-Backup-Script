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
        successful_dumps = 0
        for database in backup.get('databases'):
            db_filename = database + '.sql'

            # Dump db
            os.environ['MYSQL_PWD'] = backup.get('database_password')
            return_code = stdio.ppexec('mysqldump -u {user} --no-tablespaces {database} > {file_path}'.format(
                user=backup.get('database_user'),
                database=database,
                file_path=db_filename
            ))
            os.environ['MYSQL_PWD'] = ''

            if return_code is None or return_code > 0:
                print('   Got non-zero return code: {code}'.format(code=(return_code if return_code is not None else 'None')))
                continue

            tar.add(os.path.basename(os.path.normpath(db_filename)))
            successful_dumps = successful_dumps+1

        tar.close()

        os.chdir(saved_path)
        archive_path = os.path.join(tmp_dir, 'archive.tar.gz')

        if successful_dumps == 0:
            # No database were successfully dumped, don't return the file
            self.clean()
            return None

        return archive_path

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
