#!/usr/bin/env python

import grp
import os
import pwd
import subprocess
import tempfile
from collections import namedtuple

default_metadata = ['name', 'atime', 'ctime', 'mtime', 'user', 'group', 'permissions']
FileMetadata = namedtuple('FileMetadata', default_metadata + ['sha1', 'sha256', 'size'])
DirectoryMetadata = namedtuple('DirectoryMetadata', default_metadata)
SymlinkMetadata = namedtuple('SymlinkMetadata', default_metadata + ['native_target'])

BackupMetadata = namedtuple('BackupMetadata', ['timestamp', 'cmdline', 'files', 'symlinks', 'directories'])


def get_default_metadata(native_path):
    """Returns a dictonary, whose keys are default_metadata (as
    defined above) and entries are the results of the corresponding
    os.stat call on native_path."""

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
