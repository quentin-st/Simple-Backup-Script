import os
import re
from pathlib import Path


def get_main_class():
    return File


class File:
    key_name = "file"
    remove_artifact = False

    def find_file(self, backup):
        path = backup.get('path')

        if '*' not in path:
            # not a star expression, return it if it exists
            return path if os.path.isfile(path) else None

        # star expression
        # we assume that the star is in the filename part (/dir/prefix_*_suffix or /dir/*, not dir/*/file)
        pathinfo = Path(path)
        directory_path = pathinfo.parent

        # replace star with a regex-compatible expression: "prefix_*_suffix" => "^prefix_(.+)_suffix$"
        expr_star = pathinfo.name
        expr_regex = '^' + expr_star.replace('*', '(.+)') + '$'
        print('Regex: ', expr_regex)
        pattern = re.compile(expr_regex)

        for candidate in os.listdir(directory_path):
            candidate_path = os.path.join(directory_path, candidate)
            print('Checking ', candidate_path)
            if os.path.isfile(candidate_path):  # only handle files
                # check if filename matches
                if pattern.match(candidate):
                    # found it!
                    return candidate_path

        return None

    def create_backup_file(self, backup):
        return self.find_file(backup)

    def clean(self):
        # Nothing
        return None
