from utils import stdio


def get_main_class():
    return MySQL


class MySQL:
    key_name = "mysql"
    file_extension = "sql.gz"

    def create_backup_file(self, backup):
        # Create temporary file
        tmp_filepath = stdio.simple_exec('mktemp')

        # Dump db
        stdio.ppexec('mysqldump -u {user} -p{password} {database} | gzip > {file_path}'.format(
            user=backup.get('database_user'),
            password=backup.get('database_password'),
            database=backup.get('database'),
            file_path=tmp_filepath
        ))

        return tmp_filepath
