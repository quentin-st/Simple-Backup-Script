import os

from utils.stdio import CDIM, CRESET, CBOLD, LGREEN, print_progress


def get_main_class():
    return Ftp


class Ftp:
    def copy_to_target(self, config, target, local_filepath, target_filename):
        from ftplib import FTP

        user = target.get('user')
        password = target.get('password')
        host = target.get('host')
        port = target.get('port', 21)
        target_dir = target.get('dir')

        print('')
        print(CBOLD + LGREEN, "Connecting to {}@{}:{}...".format(user, host, port), CRESET)

        # Init FTP connection
        ftp = FTP(host, user, password)
        ftp.port = port
        print(CDIM, ftp.getwelcome(), CRESET)

        # cwd to target dir, create it if it does not exist
        target_dir = os.path.normpath(target_dir)
        target_cpnt = target_dir.split(os.sep)
        for cpnt in target_cpnt:
            # Check if it exists
            if cpnt not in ftp.nlst():
                print(CDIM, "Creating {}".format(cpnt))
                ftp.mkd(cpnt)

            ftp.cwd(cpnt)

        # Let's go
        print(CBOLD + LGREEN, "Starting transfer: {} => {}".format(local_filepath, target_filename), CRESET)
        block_size = 8192  # Default block size
        file = open(local_filepath, 'rb')
        size_total = os.fstat(file.fileno()).st_size
        global size_sent
        size_sent = 0

        def progress(bytes):
            global size_sent
            size_sent += block_size
            print_progress(size_sent, size_total)

        ftp.storbinary('STOR {}'.format(target_filename), file, callback=progress, blocksize=block_size)

        print('')
        print(CBOLD + LGREEN, "Transfer finished.", CRESET)

        # Goodbye
        try:
            ftp.quit()
        except:
            ftp.close()
