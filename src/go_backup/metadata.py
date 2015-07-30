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
    metadata['name'] = path
    # TODO: use strings instead of UNIX epoch seconds
    metadata['atime'] = os.path.getatime(native_path)
    metadata['ctime'] = os.path.getctime(native_path)
    metadata['mtime'] = os.path.getmtime(native_path)
    metadata['user'] = uid_map.get(stat.st_uid, str(stat.st_uid))
    metadata['group'] = gid_map.get(stat.st_gid, str(stat.st_gid))
    metadata['permissions'] = utils.filemode(stat.st_mode)
    return metadata


def get_file_node(rootdir, path, hash_cache, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    stat = os.lstat(native_path)

    metadata['hash'] = hash_cache[native_path]
    metadata['size'] = stat.st_size
    return FileNode(**metadata)


def get_directory_node(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)
    metadata['children'] = []
    return DirectoryNode(**metadata)


def get_symlink_node(rootdir, path, uid_map=None, gid_map=None):
    metadata = get_default_metadata(rootdir, path, uid_map=uid_map, gid_map=gid_map)

    native_path = utils.build_native_path(rootdir, path)
    metadata['target'] = os.readlink(native_path)
    return SymlinkNode(**metadata)


def get_path_parts(path):
    result = []
    cur_path = path
    while True:
        head, tail = os.path.split(cur_path)
        if tail != ""
          result.append(tail)
          cur_path = head
        else:
          break
    return reversed(result)


def get_metadata_tree(rootdir, files, symlinks, directories, digest_map, uid_map, gid_map):
   
    # Step 1: build the directory tree
    directories.sort()
    root_node = get_directory_node(rootdir, directories[0], uid_map, gid_map)
    stack = [(root_node, directories[0]]
    temp_children_dictionary = {root_node : {}}

    # TODO: add consistency checking to ensure that we are not skipping levels
    for ii in range(1, len(directories)):
        cur_name = directories[ii]

        while not cur_name.startswith(stack[-1][1]):
            stack.pop()

        new_node = get_directory_node(rootdir, cur_name, uid_map, gid_map)
        temp_children_dictionary[new_node] = {}
        parent = stack[-1][0]
        parent.children.append(new_node)
        temp_children_dictionary[parent][os.path.basename(cur_name)] = new_node
        stack.append((new_node, cur_name))

    # Step 2: insert the symlinks into the directory tree
    for linkname in symlinks:
       path_parts = get_path_parts(linkname)[:-1]
       new_node = get_symlink_node(rootdir, linkname, uid_map, gid_map)
       cur_node = root_node
       for cur_dir_name in path_parts:
          cur_node = temp_children_dictionary[cur_node][cur_dir_name]
       cur_node.children.append(new_node)

    # Step 3: insert the files into the directory tree
    for filename in files:
        path_parts = get_path_parts(filename)[:-1]
        new_node = get_symlink_node(rootdir, filename, hash_cache, uid_map, gid_map)
        cur_node = root_node
        for cur_dir_name in path_parts:
            cur_node = temp_children_dictionary[cur_node][cur_dir_name]
        cur_node.children.append(new_node)

    # Step 4: sort the lists of children
    queue = [root_node]
    while not queue.empty():
        cur_node = queue.pop()
        cur_node.children.sort()
        for child in cur_node.children:
            if isinstance(child, DirectoryNode):
                queue.append(child)

    return root_node


if __name__ == "__main__":
    pass
