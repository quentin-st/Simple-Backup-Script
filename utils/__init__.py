import hashlib

__all__ = ['stdio']


def md5(filepath):
    return hashfile(open(filepath, 'rb'), hashlib.md5())


def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()
