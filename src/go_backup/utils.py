#!/usr/bin/env python
import errno
import grp
import os.path
import pwd

def ensure_normalized(path):
    """Raise a ValueError exception if path does not equal its normalized version."""
    normalized_path = os.path.normpath(path)
    if path != normalized_path:
        raise ValueError('Path {} does not equal its normalized version {}'.format(path, normalized_path))


def ensure_absolute(path):
    """Raise a ValueError if a path is not absolute, i.e. does not start with the path separator."""
    if not path.startswith(os.sep):
        raise ValueError('Path {} is not absolute (does not start with {})'.format(path, os.sep))


def build_native_path(rootdir, path):
    """Return a native path obtained by concatenating rootdir with a
    path that's absolute in the chdir of that rootdir."""
    ensure_normalized(rootdir)
    ensure_normalized(path)
    ensure_absolute(rootdir)

    if path.startswith(os.sep):
        path = path[len(os.sep):]
    if path:
        return os.path.join(rootdir, path)
    else:
        return rootdir


def get_path_from_native_path(rootdir, native_path):
    """Return a path given a native path."""
    ensure_normalized(rootdir)
    ensure_normalized(native_path)
    ensure_absolute(rootdir)
    ensure_absolute(native_path)

    if rootdir == os.sep:
        return native_path
    elif native_path == rootdir:
        return os.sep
    elif native_path.startswith(rootdir + os.sep):
        return native_path[len(rootdir):]
    else:
        raise ValueError('Native path {} is not a valid path for root directory {}.'.format(rootdir, native_path))


def get_path_parts(path):
    """Split a path into its parts."""
    ensure_normalized(path)
    ensure_absolute(path)
    result = []
    cur_path = path
    while True:
        head, tail = os.path.split(cur_path)
        if tail != "":
          result.append(tail)
          cur_path = head
        else:
          break
    return reversed(result)


def get_uid_name_map():
    """Return a dictionary that maps numerical user ID's to user names."""
    return dict((p.pw_uid, p.pw_name) for p in pwd.getpwall())


def get_gid_name_map():
    """Return a dictionary that maps numerical group ID's to group names."""
    return dict((g.gr_gid, g.gr_name) for g in grp.getgrall())

# Backported from Python 3.3
# (http://hg.python.org/cpython/file/c440c5893d09/Lib/stat.py)
# therefore has Python license.
def filemode(mode):
    """Convert a file's mode to a string of the form '-rwxrwxrwx'."""
    import stat
    _filemode_table = (
        ((stat.S_IFLNK,              "l"),
         (stat.S_IFREG,              "-"),
         (stat.S_IFBLK,              "b"),
         (stat.S_IFDIR,              "d"),
         (stat.S_IFCHR,              "c"),
         (stat.S_IFIFO,              "p")),

        ((stat.S_IRUSR,              "r"),),
        ((stat.S_IWUSR,              "w"),),
        ((stat.S_IXUSR|stat.S_ISUID, "s"),
         (stat.S_ISUID,              "S"),
         (stat.S_IXUSR,              "x")),

        ((stat.S_IRGRP,              "r"),),
        ((stat.S_IWGRP,              "w"),),
        ((stat.S_IXGRP|stat.S_ISGID, "s"),
         (stat.S_ISGID,              "S"),
         (stat.S_IXGRP,              "x")),

        ((stat.S_IROTH,              "r"),),
        ((stat.S_IWOTH,              "w"),),
        ((stat.S_IXOTH|stat.S_ISVTX, "t"),
         (stat.S_ISVTX,              "T"),
         (stat.S_IXOTH,              "x"))
        )

    perm = []
    for table in _filemode_table:
        for bit, char in table:
            if mode & bit == bit:
                perm.append(char)
                break
        else:
            perm.append("-")
    return "".join(perm)

def mkdir_p(directory):
    """Create a directory including all subdirectories leading to it, if
    necessary. Unlike os.makedirs() this function does not raise an
    error if the directory already exists.
    """
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
