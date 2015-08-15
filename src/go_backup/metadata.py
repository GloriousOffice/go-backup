#!/usr/bin/env python

import json
import os
import subprocess
import tempfile
import utils
from collections import namedtuple

default_metadata = ['name', 'atime', 'ctime', 'mtime', 'user', 'group', 'permissions']
FileNode = namedtuple('FileMetadata', default_metadata + ['hash', 'size'])
DirectoryNode = namedtuple('DirectoryMetadata', default_metadata + ['children'])
SymlinkNode = namedtuple('SymlinkMetadata', default_metadata + ['target'])


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
    metadata['name'] = os.path.basename(path)
    # TODO: use strings instead of UNIX epoch seconds
    # TODO: fields we are currently not using: st_mode, st_ino, st_dev, st_nlink
    #       - is this intentional?
    metadata['atime'] = stat.st_atime
    metadata['ctime'] = stat.st_ctime
    metadata['mtime'] = stat.st_mtime
    metadata['user'] = uid_map.get(stat.st_uid, str(stat.st_uid))
    metadata['group'] = gid_map.get(stat.st_gid, str(stat.st_gid))
    metadata['permissions'] = '%04o' % stat.st_mode
    return metadata


def get_file_node(rootdir, path, hash_cache, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    stat = os.lstat(native_path)

    metadata['hash'] = hash_cache[path]
    metadata['size'] = stat.st_size
    return FileNode(**metadata)


def get_directory_node(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)
    metadata['children'] = {}
    return DirectoryNode(**metadata)


def get_symlink_node(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    metadata['target'] = os.readlink(native_path)
    return SymlinkNode(**metadata)


def get_metadata_tree(rootdir, files, symlinks, directories, digest_map, uid_map, gid_map):
    # Step 0: empty tree
    root_node = get_directory_node(rootdir, os.sep, uid_map, gid_map)

    def find_directory_in_tree(root, dirname):
        path_parts = utils.get_path_parts(dirname)
        cur_path = os.sep
        cur_node = root
        for part in path_parts:
            cur_path = os.path.join(cur_path, part)
            if part not in cur_node.children:
                new_node = get_directory_node(rootdir, cur_path, uid_map, gid_map)
                cur_node.children[part] = new_node
            cur_node = cur_node.children[part]
        return cur_node

    # Step 1: insert the directories into the directory tree
    for full_dirname in directories:
        dirname, basename = os.path.split(full_dirname)
        if not basename:
            # we have handled the root directory separately
            assert dirname == os.sep
            continue
        # Navigate to the right part in the directory tree
        dir_node = find_directory_in_tree(root_node, dirname)
        # Insert the directory node
        new_node = get_directory_node(rootdir, full_dirname, uid_map, gid_map)
        dir_node.children[basename] = new_node

    # Step 2: insert the symlinks into the directory tree
    for linkname in symlinks:
        dirname, basename = os.path.split(linkname)
        # Navigate to the right part in the directory tree
        dir_node = find_directory_in_tree(root_node, dirname)
        # Insert the symlink node
        new_node = get_symlink_node(rootdir, linkname, uid_map, gid_map)
        dir_node.children[basename] = new_node

    # Step 3: insert the files into the directory tree
    for filename in files:
        dirname, basename = os.path.split(filename)
        # Navigate to the right part in the directory tree
        dir_node = find_directory_in_tree(root_node, dirname)
        # Insert the file node
        new_node = get_file_node(rootdir, filename, digest_map, uid_map, gid_map)
        dir_node.children[basename] = new_node

    return root_node


if __name__ == "__main__":
    pass
