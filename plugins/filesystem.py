import tarfile
import os
import shutil

from utils import stdio
from utils.stdio import CRESET, CBOLD, LGREEN


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

        # cd to temp dir
        saved_path = os.getcwd()
        os.chdir(tmp_dir)

        # Create tar file
        tar = tarfile.open('archive.tar.gz', 'w:gz')

        # Loop over directories
        for directory in backup.get('directories'):
            dir_name = os.path.basename(os.path.normpath(directory))

            # Create single tar.gz file for this dir
            singletar_filename = dir_name + ".tar.gz"
            print(CBOLD+LGREEN, "\nCreating " + singletar_filename, CRESET)

            single_tar = tarfile.open(singletar_filename, 'w:gz')
            single_tar.add(directory, arcname=dir_name)
            single_tar.close()

            # Add it to global tar file
            tar.add(singletar_filename, arcname=dir_name)

        tar.close()

        os.chdir(saved_path)

        return tmp_dir + '/archive.tar.gz'

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
