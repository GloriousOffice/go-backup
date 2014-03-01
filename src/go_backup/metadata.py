#!/usr/bin/env python

import json
import os
import subprocess
import tempfile
import utils
from collections import namedtuple

default_metadata = ['name', 'atime', 'ctime', 'mtime', 'user', 'group', 'permissions']
FileMetadata = namedtuple('FileMetadata', default_metadata + ['sha1', 'sha256', 'size'])
DirectoryMetadata = namedtuple('DirectoryMetadata', default_metadata)
SymlinkMetadata = namedtuple('SymlinkMetadata', default_metadata + ['native_target'])

BackupMetadata = namedtuple('BackupMetadata', ['files', 'symlinks', 'directories'])


def get_default_metadata(rootdir, path, uid_map=None, gid_map=None):
    """Returns a dictonary, whose keys are default_metadata (as
    defined above) and entries are the results of the corresponding
    os.stat call on native_path."""
    if uid_map is None:
        uid_map = utils.get_uid_name_map()
    if gid_map is None:
        gid_map = utils.get_gid_name_map()
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


def get_backup_metadata(rootdir, files, symlinks, directories, digest_map, uid_map=None, gid_map=None):
    metadata_files = [get_file_metadata(rootdir, p, digest_map=digest_map, uid_map=uid_map, gid_map=gid_map) for p in files]
    metadata_symlinks = [get_symlink_metadata(rootdir, p, uid_map=uid_map, gid_map=gid_map) for p in symlinks]
    metadata_directories = [get_directory_metadata(rootdir, p, uid_map=uid_map, gid_map=gid_map) for p in directories]
    return BackupMetadata(files=metadata_files, symlinks=metadata_symlinks, directories=metadata_directories)


def write_backup_metadata(f, metadata):
    d = {'files': [t.__dict__ for t in metadata.files],
         'symlinks': [t.__dict__ for t in metadata.symlinks],
         'directories': [t.__dict__ for t in metadata.directories]}
    json.dump(d, f, indent=4, separators=(',', ': '))


def read_backup_metadata(f):
    d = json.load(f)
    if set(d.keys()) != set(BackupMetadata._fields):
        raise ValueError(("Set of backup metadata keys ('%s') does not match expected ('%s')." %
                          (sorted(d.keys()), sorted(BackupMetadata._fields))))
    metadata = BackupMetadata(files=[FileMetadata(**m) for m in d['files']],
                              symlinks=[SymlinkMetadata(**m) for m in d['symlinks']],
                              directories=[DirectoryMetadata(**m) for m in d['directories']])
    return metadata


if __name__ == "__main__":
    pass
