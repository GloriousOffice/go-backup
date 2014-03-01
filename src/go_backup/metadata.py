#!/usr/bin/env python

import grp
import os
import pwd
import subprocess
import tempfile
import utils
from collections import namedtuple

default_metadata = ['name', 'atime', 'ctime', 'mtime', 'user', 'group', 'permissions']
FileMetadata = namedtuple('FileMetadata', default_metadata + ['sha1', 'sha256', 'size'])
DirectoryMetadata = namedtuple('DirectoryMetadata', default_metadata)
SymlinkMetadata = namedtuple('SymlinkMetadata', default_metadata + ['native_target'])

BackupMetadata = namedtuple('BackupMetadata', ['timestamp', 'cmdline', 'files', 'symlinks', 'directories'])


def get_default_metadata(rootdir, path, uid_map=None, gid_map=None):
    """Returns a dictonary, whose keys are default_metadata (as
    defined above) and entries are the results of the corresponding
    os.stat call on native_path."""
    if uid_map is None:
        uid_map = get_uid_name_map()
    if gid_map is None:
        gid_map = get_gid_name_map()
    native_path = utils.build_native_path(rootdir, path)
    stat = os.lstat(native_path)

    metadata = {}
    metadata['name'] = path
    metadata['atime'] = os.path.getatime(native_path)
    metadata['ctime'] = os.path.getctime(native_path)
    metadata['mtime'] = os.path.getmtime(native_path)
    metadata['user'] = uid_map.get(stat.st_uid, str(stat.st_uid))
    metadata['group'] = gid_map.get(stat.st_gid, str(stat.st_gid))
    metadata['permissions'] = utils.filemode(stat.st_mode)
    return metadata


def get_file_metadata(rootdir, path, digest_map, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    stat = os.lstat(native_path)

    metadata['sha1'] = digest_map[path].sha1
    metadata['sha256'] = digest_map[path].sha256
    metadata['size'] = stat.st_size
    return FileMetadata(**metadata)


def get_directory_metadata(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)
    return DirectoryMetadata(**metadata)


def get_symlink_metadata(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    metadata['native_target'] = os.readlink(native_path)
    return SymlinkMetadata(**metadata)


def get_uid_name_map():
    """Return a dictionary that maps numerical user ID's to user
    names."""
    return dict((p.pw_uid, p.pw_name) for p in pwd.getpwall())


def get_gid_name_map():
    """Return a dictionary that maps numerical group ID's to group
    names."""
    return dict((g.gr_gid, g.gr_name) for g in grp.getgrall())

if __name__ == "__main__":
    pass
