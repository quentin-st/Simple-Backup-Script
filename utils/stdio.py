import sys
import os
import threading
from subprocess import Popen, PIPE, STDOUT

CRESET = "\033[0m"
CDIM   = "\033[2m"
CBOLD  = "\033[1m"
LGREEN = "\033[92m"
LWARN  = "\033[93m"


def ppexec(cmd: str, env = None) -> int:
    print("    [$ {}]".format(cmd))
    empty_line = bytes()

    child = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True, env=env)
    for line in child.stdout:
        line = line.strip()
        if line == empty_line:
            continue
        print(CDIM, "   " + line.decode("utf-8"), CRESET)

    return child.poll()


def simple_exec(cmd, args=None):
    return Popen([cmd, args] if args else cmd, stdout=PIPE).communicate()[0].decode('UTF-8').strip()


def _print_progress(progress):
    sys.stdout.write("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(progress * 50), progress * 100))
    sys.stdout.flush()


def print_progress(transferred, total):
    progress = transferred/total
    _print_progress(progress)


class ProgressPercentage(object):
    """
    See https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html#the-callback-parameter
    """
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            _print_progress(percentage / 100)
