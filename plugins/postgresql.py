from utils import stdio


class PostgreSQL:
    key_name = "postgresql"

    def create_backup_file(self, backup):
        # Create temporary file
        tmp_filepath = stdio.simple_exec('mktemp')

        # Dump db
        stdio.ppexec('pg_dump -Fc {database} > {file_path}'.format(
            database=backup.get('database'),
            file_path=tmp_filepath
        ))

        return tmp_filepath
