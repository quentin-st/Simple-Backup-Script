from utils import stdio


def get_main_class():
    return MySQL


class MySQL:
    key_name = "mysql"
    file_extension = "tar.gz"

    def create_backup_file(self, backup):
        # Create temporary directory
        tmp_dir = stdio.simple_exec('mktemp',  '--directory')

        # Loop over databases
        for database in backup.get('databases'):
            db_filepath = tmp_dir + '/' + database + '.sql'
            # Dump db
            stdio.ppexec('mysqldump -u {user} -p{password} {database} | gzip > {file_path}'.format(
                user=backup.get('database_user'),
                password=backup.get('database_password'),
                database=database,
                file_path=db_filepath
            ))

        # Create temp file
        tmp_file = stdio.simple_exec('mktemp')

        # Compress temp directory
        stdio.ppexec('cd {dir} && tar -cvzf {file} ./*'.format(
            file=tmp_file,
            dir=tmp_dir
        ))

        return tmp_file
