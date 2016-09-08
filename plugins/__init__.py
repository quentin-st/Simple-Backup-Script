import sys
import inspect
from plugins import postgresql, mysql, filesystem

__all__ = ['postgresql', 'mysql', 'filesystem']


def get_supported_backup_profiles():
    plugins_list = {}

    for name, obj in inspect.getmembers(sys.modules[__name__], inspect.ismodule):
        if hasattr(obj, 'get_main_class'):
            # Get class from this member
            plugins_list[name] = obj.get_main_class()

    return plugins_list
