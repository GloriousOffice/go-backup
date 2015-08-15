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
    return list(reversed(result))


def get_uid_name_map():
    """Return a dictionary that maps numerical user ID's to user names."""
    return dict((p.pw_uid, p.pw_name) for p in pwd.getpwall())


def get_gid_name_map():
    """Return a dictionary that maps numerical group ID's to group names."""
    return dict((g.gr_gid, g.gr_name) for g in grp.getgrall())


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
