#!/usr/bin/env python
import os
import utils

VerificationResult = namedtuple('VerificationResult', ['changed', 'missing',
                                                       'unexpected',
                                                       'scan_errors'])

ScanResult = namedtuple('ScanResult', ['files', 'symlinks', 'directories',
                                       'errors', 'ignored'])
ComparisonResult = namedtuple('ComparisonReslut', ['changed', 'missing',
                                                   'unexpected'])

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


def verify_files(rootdir, files, file_metadata):


def verify_symlinks(rootdir, symlinks, symlink_metadata):
    original_symlinks = set([x.name for x in symlink_metadata])
    current_symlinks = set(symlinks)
    missing = original_symlinks - current_symlinks
    unexpected = current_symlinks - original_symlinks
    changed = []
    for link in original_symlinks.intersection(current_symlinks):
        current_target = os.readlink(utils.
    return ComparisonResult([], sorted(list(missing)), sorted(list(unexpected)))


def verify_directories(rootdir, directories, directories_metadata):
    original_directories = set([x.name for x in directories_metadata])
    current_directories = set(directories)
    missing = original_directories - current_directories
    unexpected = current_directories - original_directories
    return ComparisonResult([], sorted(list(missing)), sorted(list(unexpected)))


def verify_backup(rootdir, metadata):
    # Results
    changed = []
    missing = []
    unexpected = []
    scan_errors = []

    # First, we get all the relevant paths
    scan_result = scan_backup(rootdir)
    scan_errors = scan_result.errors
    unexpected = scan_result.ignored

    # Verify the files
    files_result = verify_files(rootdir, scan_result.files, metadata.files)
    changed.append(files_result.changed)
    missing.append(files_result.missing)
    unexpected.append(files_result.unexpected)
    
    # Verify the symlinks
    symlinks_result = verify_symlinks(rootdir, scan_result.symliks,
                                      metadata.symlinks)
    changed.append(symlinks_result.changed)
    missing.append(symlinks_result.missing)
    unexpected.append(symlinks_result.unexpected)

    # Verify the directories
    directories_result = verify_directories(rootdir, scan_result.directories,
                                            metadata.directories)
    changed.append(directories_result.changed)
    missing.append(directories_result.missing)
    unexpected.append(directories_result.unexpected)

    # Return the final result
    return VerificationResult(changed, missing, unexpected, scan_errors)
