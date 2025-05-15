import tarfile
import os
import shutil
import subprocess
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

        # Parse database configuration
        databases = backup.get('databases')
        mysql_user_username = backup.get('database_user')
        mysql_user_password = backup.get('database_password')

        if databases == '*':
            # List available databases
            completed_process = subprocess.run(
                ['mysql', '-u', mysql_user_username, '--silent', '--raw', '--skip-column-names', '-e', 'SHOW DATABASES;'],
                capture_output=True,
                text=True,
                check=True,
                env=dict(os.environ, MYSQL_PWD=mysql_user_password)
            )
            output = completed_process.stdout.strip('\n')
            databases = output.split('\n')

            # Remove system databases
            databases.remove('mysql')
            databases.remove('information_schema')
            databases.remove('performance_schema')
            databases.remove('sys')

        # Loop over databases
        successful_dumps = 0
        for database in databases:
            db_filename = database + '.sql'

            # Dump db
            return_code = stdio.ppexec('mysqldump -u {user} --no-tablespaces {database} > {file_path}'.format(
                user=mysql_user_username,
                database=database,
                file_path=db_filename,
            ), env=dict(os.environ, MYSQL_PWD=mysql_user_password))

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
