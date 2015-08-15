#!/usr/bin/env python
"""go-backup content-addressable storage

This module implements a filesystem-backed content-addressable storage
manager.

Everywhere below HASH(x) refers to go_backup.hashing.hash_fileobj(x).

The depth of the filesystem storage sharding is set at class
initialization, and defaults to 2. This results in 4096*256**N bytes
of overhead, or about 268MB on a traditional UNIX filesystem like ext4
for an empty CAS.

A sharding depth of 1 will reduce the initial overhead, but storing
large amounts of files may result in the directories taking on more
blocks. Since each filename will be approx. 64 characters (less 2N for
sharding) and a directory entry has an overhead of 8 bytes,
approximately 56 files per directory can be stored.  With a sharding
level of 1, this holds approximately 14K files before directories are
over-subscribed.  Since most home directories are expected to hold
more files, the sharding is recommended to be set to 2, which will
hold 3.6M files. A sharding of 3 or higher is not recommended.
"""

import hashing
import itertools
import os
import shutil
import utils

class CAS(object):

    NIBBLES_PER_SHARD = 2

    def __init__(self, root, sharding=2):
        """Create a new CAS.

        The CAS class is initialized by two main parameters: the root
        of the CAS tree, and the sharding level. These parameters must
        stay consistent throughout the lifetime of the CAS or files
        will be incorrectly placed. This class does not implement
        in-place, native re-sharding.

        Args:
          root: Absolute path to the root directory of the CAS
          sharding: The depth of the sharding in the CAS. Defaults to 2.
        """
        # wrap in str() as PyTest's LocalPath does not have e.g. startswith()
        self._root = str(root)
        self._sharding = sharding

        assert self._root == os.path.abspath(self._root)

    def _get_cas_path_components(self, hash_digest):
        """Compute the file system path components corresponding to this hash
        digest at the specified sharding level.

        Args:
          hash_digest: Hash digest to compute the path components for.

        Returns:
          File system path components for hash_digest. The components
          are relative to the root of the CAS.
        """
        path_components = []
        for shard_level in xrange(self._sharding):
            path_components.append(
                hash_digest[shard_level * CAS.NIBBLES_PER_SHARD:
                            (shard_level + 1) * CAS.NIBBLES_PER_SHARD])
        path_components.append(hash_digest[self._sharding * CAS.NIBBLES_PER_SHARD:])

        assert ''.join(path_components) == hash_digest

        return path_components

    def _get_cas_path(self, hash_digest):
        """Compute the absolute file system path corresponding to this hash
        digest at the specified sharding level.

        Args:
          hash_digest: Hash digest to compute the path for.

        Returns:
          File system path for hash_digest.
        """
        return os.path.join(self._root, os.path.join(
            *self._get_cas_path_components(hash_digest)))

    def has_file(self, hash_digest):
        """Check if the specified file exists in the CAS.

        Args:
          hash_digest: Hash of the file.

        Returns:
          True if the file with hash hash_digest is present in the CAS
          and False otherwise.
        """
        return os.path.exists(self._get_cas_path(hash_digest))

    def store(self, fileobj, hash_digest):
        """Store the specified file in the CAS.

        This method stores the specified file in the CAS. The
        hash_digest provided is assumed to be correct (i.e. equal to
        HASH on the file contents).

        Args:
          fileobj: File-like object to store in CAS.
          hash_digest: Hash digest of the file.

        Returns:
          This function raises LookupError if the specified file is
          already in the CAS.
        """
        if self.has_file(hash_digest):
            raise LookupError("File already present in the CAS.")

        destination_path = self._get_cas_path(hash_digest)
        destination_dir = os.path.dirname(destination_path)
        utils.mkdir_p(destination_dir)

        with open(destination_path, 'wb') as destination_fileobj:
            shutil.copyfileobj(fileobj, destination_fileobj)

    def retrieve(self, hash_digest):
        """Retrieves the file specified by its digest from the CAS and returns
        a file-like object.

        Args:
          hash_digest: Hash digest of the file to be retrieved.

        Returns:
          File-like object containing the desired data. Raises
          LookupError if the specified file is not in the CAS.
        """
        if not self.has_file(hash_digest):
            raise LookupError("File not present in the CAS.")

        return open(self._get_cas_path(hash_digest), 'rb')

    def list(self):
        """Returns the list of hashes of all files in the CAS.

        Returns:
           The list of hashes. The order in the list is unspecified.
        """
        return list(self.ilist())

    def ilist(self):
        """Return an iterator of hashes of all files in CAS.

        Return:
           The iterator of hashes. The iteration order is unspecified.
        """
        for (dirpath, dirnames, filenames) in os.walk(self._root):
            # All files in uncorrupted CAS were previously stored
            # by a .store() call, so we construct the hashes by
            # joining shards encoded in dirpath and the file names.
            path_parts = utils.get_path_parts(dirpath)
            shard_parts = path_parts[-self._sharding:]

            for hash_without_shards in filenames:
                full_hash = ''.join(shard_parts) + hash_without_shards
                yield full_hash
