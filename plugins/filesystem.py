import tarfile
import os
import shutil

from utils import stdio


def get_main_class():
    return Filesystem


class Filesystem:
    key_name = "filesystem"
    file_extension = "tar.gz"

    def __init__(self):
        self.temp_dir = ''

    def create_backup_file(self, backup):
        # Create temporary working directory
        tmp_dir = stdio.simple_exec('mktemp',  '--directory')
        self.temp_dir = tmp_dir

        # Create tar file
        saved_path = os.getcwd()
        os.chdir(tmp_dir)

        tar = tarfile.open('archive.tar.gz', 'w:gz')

        # Loop over directories
        for directory in backup.get('directories'):
            tar.add(directory, arcname=os.path.basename(os.path.normpath(directory)))

        tar.close()

        os.chdir(saved_path)

        return tmp_dir + '/archive.tar.gz'

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
