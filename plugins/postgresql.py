from utils import stdio


def get_main_class():
    return PostgreSQL


class PostgreSQL:
    key_name = "postgresql"
    file_extension = "tar.gz"

    def create_backup_file(self, backup):
        # Create temporary directory
        tmp_dir = stdio.simple_exec('mktemp', '--directory')

        # Loop over databases
        for database in backup.get('databases'):
            db_filepath = tmp_dir + '/' + database + '.sql'
            # Dump db
            stdio.ppexec('pg_dump {database} -U {user} -h localhost -f {file_path} --no-password'.format(
                database=database,
                user=backup.get('database_user', database),
                file_path=db_filepath
            ))

        # Create temp file
        tmp_file = stdio.simple_exec('mktemp')

        # Compress temp directory
        stdio.ppexec('cd {dir} && tar -cvzf {file} ./*'.format(
            dir=tmp_dir,
            file=tmp_file
        ))

        return tmp_file
