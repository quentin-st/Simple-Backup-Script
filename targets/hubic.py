import os

from utils import md5
from utils.stdio import CRESET, CBOLD, CDIM, LGREEN, LWARN


def get_main_class():
    return Hubic


class Hubic:
    def copy_to_target(self, config, target, local_filepath, target_filename):
        from lib import lhubic

        hubic = lhubic.Hubic(
            client_id=target.get('client_id'),
            client_secret=target.get('client_secret')
        )
        hubic.os_auth()

        container = target.get('container', 'default')
        target_filepath = os.path.join(target.get('dir', '/Backups/'), target_filename)

        # Upload file
        with open(local_filepath, 'rb') as fh:
            print(CBOLD + LGREEN, "Starting transfer: {} => {}".format(local_filepath, target_filename), CRESET)

            md5_hash = hubic.put_object(container, target_filepath, fh.read())

            print(CBOLD + LGREEN, "Transfer finished.", CRESET)

        print(CDIM, 'Computing file hash...', CRESET)
        if md5_hash != md5(local_filepath):
            message = 'Warning: hash mismatch for {}'.format(target_filename)
            print(LWARN + CBOLD, message, CRESET)
            return message

        print(CDIM + LGREEN, 'Hash matches!', CRESET)
        return True
