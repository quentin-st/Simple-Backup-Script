from utils import stdio


def get_main_class():
    return PostgreSQL


class PostgreSQL:
    key_name = "postgresql"
    file_extension = "sql"

    def create_backup_file(self, backup):
        # Create temporary file
        tmp_filepath = stdio.simple_exec('mktemp')

        # Dump db
        stdio.ppexec('pg_dump {database} -U {user} -h localhost -f {file_path} --no-password'.format(
            database=backup.get('database'),
            user=backup.get('database_user', backup.get('database')),
            file_path=tmp_filepath
        ))

        return tmp_filepath
