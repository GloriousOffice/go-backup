#!/usr/bin/env python
"""go-backup content-addressable storage

This module implements a filesystem-backed content-addressable storage
manager, using sha256 from hashlib.

Everywhere below HASH(x) refers to hashlib.sha256(x).hexdigest().

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

import errno
import hashlib
import itertools
import os
import shutil

class CAS(object):

    NIBBLES_PER_SHARD = 2
    READ_BLOCK_SIZE = 1024 * 1024  # 1 mebibyte

    def __init__(self, root, sharding=2):
        """Create a new CAS.

        The CAS class is initialzied by two main parameters: the root
        of the CAS tree, and the sharding level. These parameters must
        stay consistent throughout the lifetime of the CAS or files
        will be incorrectly placed. This class does not implement
        in-place, native re-sharding.

        Args:
          root: Path to the root directory of the CAS
          sharding: The depth of the sharding in the CAS. Defaults to 2.
        """
        self._root = root
        self._sharding = sharding

    @staticmethod
    def shard_generator():
        DIRS_PER_SHARD = 16 ** CAS.NIBBLES_PER_SHARD
        DIR_FORMAT_STR = '%%0%dx' % (CAS.NIBBLES_PER_SHARD,)

        for i in xrange(DIRS_PER_SHARD):
            yield DIR_FORMAT_STR % (i,)

    @staticmethod
    def mkdir_p(directory):
        # TODO(madars): move this into a utility module
        try:
            os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e

    def prepare(self):
        """Prepare the CAS for operation by creating initial directories.

        This method creates the directories required by the sharding
        level. It is safe to run even on existing CAS structures; the
        directory creation is idempotent.
        """
        generators = itertools.tee(CAS.shard_generator(), self._sharding)
        for i in itertools.product(*generators):
            CAS.mkdir_p(os.path.join(self._root, os.path.join(*i)))

    @staticmethod
    def HASH(io):
        hasher = hashlib.sha256()
        while True:
            data = io.read(CAS.READ_BLOCK_SIZE)
            if not data:
                break
            hasher.update(data)
        return hasher.hexdigest()

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

    def get_cas_path(self, hash_digest):
        """Compute the absolute file system path corresponding to this hash
        digest at the specified sharding level.

        Args:
          hash_digest: Hash digest to compute the path for.

        Returns:
          File system path for hash_digest.
        """
        return os.path.join(self._root, os.path.join(
            *self._get_cas_path_components(hash_digest)))

    def store(self, filename, hash_digest=None):
        """Store the specified file in the CAS.

        This method stores the file pointed to by the file name in the
        CAS. If hash digest is provided, it is assumed to be correct
        (i.e. equal to HASH on the file contents), otherwise it is
        computed.

        Args:
          filename: Path to the file to store in the CAS.
          hash_digest: Advice for hash digest of the file. Defaults to None.

        Returns:
          The digest of the file, if stored succesfully, and raise an
          exception otherwise.
        """
        if not hash_digest:
            with open(filename, 'rb') as io:
                hash_digest = CAS.HASH(io)

        destination_path = self.get_cas_path(hash_digest)
        shutil.copyfile(filename, destination_path)

        return hash_digest

    def retrieve(self, hash_digest):
        """Retrieves the file specified by its digest from the CAS and returns
        a file-like object.

        To get file name use get_cas_path.

        Args:
          hash_digest: Hash digest of the file to be retrieved.

        Returns:
          File-like object containing the desired data.
        """
        return open(self.get_cas_path(hash_digest), 'rb')

if __name__ == '__main__':
    c = CAS('/tmp/something')
    c.prepare()
    digest = c.store('/etc/hosts')
    with c.retrieve(digest) as hosts:
        print hosts.read()
