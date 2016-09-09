import os
import shutil

from utils.stdio import CRESET, CBOLD, LGREEN


def get_main_class():
    return Local


class Local:
    def copy_to_target(self, config, target, local_filepath, target_filename):
        target_dir = target.get('dir')
        target_path = os.path.join(target_dir, target_filename)

        print(CBOLD + LGREEN, "Starting local copy: {} => {}".format(local_filepath, target_path), CRESET)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        shutil.copy(local_filepath, target_path)
