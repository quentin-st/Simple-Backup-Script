import tarfile
import os
import shutil
import tempfile

from utils.stdio import CRESET, CBOLD, LGREEN, LWARN


def get_main_class():
    return Filesystem


class Filesystem:
    key_name = "filesystem"
    file_extension = "tar.gz"

    def __init__(self):
        self.temp_dir = ''

    def create_backup_file(self, backup):
        # Create temporary working directory
        tmp_dir = tempfile.mkdtemp()
        self.temp_dir = tmp_dir

        # cd to temp dir
        saved_path = os.getcwd()
        os.chdir(tmp_dir)

        # Create tar file
        tar = tarfile.open('archive.tar.gz', 'w:gz')

        # Pre-process directories list
        directories = []
        for directory in backup.get('directories'):
            # [/var/www/*] must be replaced with [/var/www/dir1/, /var/www/dir2/],
            if directory.endswith('*'):
                real_name = directory[:-1]
                for name in os.listdir(real_name):
                    if os.path.isdir(os.path.join(real_name, name)):
                        directories.append(os.path.join(real_name, name))
            # Handle "-/var/www/not-this/"
            elif directory.startswith('-'):
                dir_name = directory[1:].rstrip('/')
                if dir_name in directories:
                    directories.remove(dir_name)
                else:
                    print(LWARN, "    Useless directory exclude pattern {}: directory wasn't selected at first".format(dir_name))
            else:
                directories.append(directory)

        # Loop over directories
        for directory in directories:
            dir_name = os.path.basename(os.path.normpath(directory))

            # Create single tar.gz file for this dir
            singletar_filename = dir_name + ".tar.gz"
            print("    + " + singletar_filename)

            single_tar = tarfile.open(singletar_filename, 'w:gz')
            single_tar.add(directory, arcname=dir_name)
            single_tar.close()

            # Add it to global tar file
            tar.add(singletar_filename, arcname=dir_name)

        tar.close()

        os.chdir(saved_path)

        return os.path.join(tmp_dir, 'archive.tar.gz')

    def clean(self):
        if self.temp_dir and os.path.isdir(self.temp_dir):
            shutil.rmtree(self.temp_dir)
