#!/usr/bin/env python
"""go-backup's choice of hash function and related utilities.

The hash function of choice in go-backup is SHA256. This module
provides an agnostic way to refer to SHA256; all other code should use
methods implemented here and never compute hashes on their own.
"""

import hashlib
import multiprocessing

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

def _hash_file(fn):
    """Helper function for hash_list_of_files. Semantically this would
    belong inside its caller, but multiprocessing expects the
    functions to be globally visible (see
    https://stackoverflow.com/questions/3288595/)
    """
    with open(fn, "rb") as file:
        return (fn, hash_fileobj(file))

def hash_list_of_files(file_list, num_processes=None):
    """Given a list of file names, compute and return hashes of all files
    in the list.

    Args:
      file_list: List of file names to hash.
      num_processes: Number of parallel processes to use for
      hashing. Defaults to number of cores in system.

    Returns:
      Dictionary d of hashes. For each file name fn in file_list, the
      value d[fn] equals hash of file fn.
    """
    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    pool = multiprocessing.Pool(num_processes)
    result = {}

    try:
        for fn, digest in pool.imap_unordered(_hash_file, file_list):
            result[fn] = digest
        # clean up
        pool.close()
        pool.join()
    except KeyboardInterrupt:
        pool.terminate()
        pool.join()

    return result

if __name__ == '__main__':
    # When invoked as an executable, hashing.py emulates output of
    # sha256deep -f file_list. Empirically, the performance of
    # hashing.py matches or exceeds that of sha256deep both for
    # scenarios with small and large files. (This is probably
    # attributed to optimized OpenSSL implementation used by hashlib;
    # hashdeep uses slower reference implementation.)
    import sys
    lst = [fn.strip() for fn in open(sys.argv[1]).read().split("\n") if fn.strip()]
    hashes = hash_list_of_files(lst)
    for fn in lst:
        print "%s  %s" % (hashes[fn], fn)
