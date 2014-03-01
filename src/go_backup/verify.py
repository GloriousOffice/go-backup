#!/usr/bin/env python
import os
import utils

VerificationResult = namedtuple('VerificationResult', ['changed', 'missing',
                                                       'unexpected',
                                                       'scan_errors'])

ScanResult = namedtuple('ScanResult', ['files', 'symlinks', 'directories',
                                       'errors', 'ignored'])

def scan_backup(rootdir):
    files = []
    symlinks = []
    directories = []
    errors = []
    ignored = []

    def listdir_onerror(error):
        errors.append(error)

    rootdir = os.path.normpath(rootdir)

    # Now recursively traverse the file system
    for root, dirs, files in os.walk(rootdir,
                                     topdown=True,
                                     onerror=listdir_onerror,
                                     followlinks=False):
        for f in itertools.chain(files, dirs):
            native_path = os.path.join(root, f)
            path = utils.get_path_from_native_path(rootdir, native_path)
            if path == '/.go_backup':
                ignored.append(path)
            elif os.path.isfile(native_path):
                files.append(path)
            elif os.path.islink(native_path):
                symlinks.append(path)
            elif os.path.isdir(native_path):
                directories.append(path)
            else:
                ignored.append(path)
        # Also, we remove all mount points from dirs so that os.walk does not
        # recurse into a different file system.
        dirs[:] = [d for d in dirs if not os.path.ismount(os.path.join(rootdir, d))]

    return ScanResult(files, symlinks, directories, errors, ignored)


strict_metadata = ['atime', 'mtime', 'ctime', 'user', 'group', 'permissions']

def lenient_metadata_dictionary(metadata):
    d = metadata._asdict()
    result = {}
    for k in d.keys():
        if k not in strict_metadata:
            result[k] = d[d]
    return result


def lenient_match(metadata1, metadata2):
    return lenient_metadata_dictionary(metadata1)
        == lenient_metadata_dictionary(metadata2)


def verify_backup(rootdir, metadata, num_threads=None):
    # Results
    changed = []
    missing = []
    unexpected = []
    scan_errors = []

    # First, we get all the relevant paths
    scan_result = scan_backup(rootdir)
    scan_errors = scan_result.errors
    unexpected = scan_result.ignored

    # Build a dictionary with all original metdata
    original_metadata = {}
    for p in itertools.chain(metadata.files, metadata.symlinks,
                             metadata.directories):
        original_metadata[p.name] = p

    # Build a dictionary with all current metadata
    digest_map = hashdeep.compute_digests(rootdir, scan_result.filenames,
                                          num_threads)
    uid_map = utils.get_uid_name_map()
    gid_map = utils.get_gid_name_map()
    current_metadata = {}
    for f in scan_result.files:
        current_metadata[f] = metadata.get_file_metadata(rootdir, f, digest_map,
                                                         uid_map, gid_map)
    for s in scan_result.symlinks:
        current_metadata[s] = metadata.get_symlink_metadata(rootdir, f, uid_map,
                                                            gid_map)
    for d in scan_results.dictionaries:
        current_metadata[d] = metadata.get_directory_metadata(rootdir, f,
                                                              uid_map, gid_map)

    # Find missing and unexpected files
    all_current_paths = set(scan_result.files + scan_result.symlinks
                                              + scan_result.directories)
    all_original_paths = set(metadata.keys())

    missing = sorted(list(all_original_paths - all_current_paths))
    unexpected.append(list(all_current_paths - all_original_paths))
    unexpected.sort()

    # Find changed files
    for p in all_current_paths.intersection(all_original_paths):
        if not lenient_match(current_metadata[p], original_metadata[p]):
            changed.append(p)

    # Return the final result
    return VerificationResult(changed, missing, unexpected, scan_errors)


if __name__ == '__main__':
    import sys
    rootdir = sys.argv[1]
    metadatafile = sys.argv[2]
    with open(metadatafile, 'r') as f:
        metadata = metadata.read_backup_metadata(f)
    res = verify_backup(rootdir, metadata)
    print res
