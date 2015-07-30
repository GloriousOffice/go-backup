#!/usr/bin/env python
"""go-backup's choice of hash function and related utilities.

The hash function of choice in go-backup is SHA256. This module
provides an agnostic way to refer to SHA256; all other code should use
methods implemented here and never compute hashes on their own.
"""

import hashlib

READ_BLOCK_SIZE = 1024 * 1024  # 1 mebibyte

def hash_str(str):
    """Compute and return the SHA256 digest of a string."""
    return hashlib.sha256(str).hexdigest()

def hash_fileobj(fileobj):
    """Compute and return the SHA256 digest of a file-like object."""
    hasher = hashlib.sha256()
    while True:
        data = fileobj.read(READ_BLOCK_SIZE)
        if not data:
            break
        hasher.update(data)
    return hasher.hexdigest()
