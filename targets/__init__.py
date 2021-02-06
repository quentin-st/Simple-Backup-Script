import sys
import inspect
from targets import local, remote, ftp

__all__ = ['local', 'remote', 'ftp']


def get_supported_targets():
    targets_list = {}

    for name, obj in inspect.getmembers(sys.modules[__name__], inspect.ismodule):
        if hasattr(obj, 'get_main_class'):
            # Get class from this member
            targets_list[name] = obj.get_main_class()

    return targets_list
