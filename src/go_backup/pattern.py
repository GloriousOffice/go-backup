#!/usr/bin/env python
import itertools
import os
import re
import utils
from collections import namedtuple

"""The data structure containing matching results for given patterns."""
MatchingResult = namedtuple('MatchingResult', ['filenames', 'symlinks', 'directories', 'errors', 'ignored'])

"""Constants indicating whether a pattern should be included or excluded."""
INCLUDE = 1
EXCLUDE = 2

def parse_pattern_file(f):
    """Return a list of patterns parsed from the file object f

    The patterns are returned as a list of pairs (modifier, pattern), where
    modifier is either the constant INCLUDE or the constant EXCLUDE. pattern
    is the pathname affected by the inclusion / exclusion rule. The list is
    in the same order as the pattern file f, i.e., in order of priority (later
    rules override earlier rules).

    In case of an invalid pattern, the function raises a ValueError exception.
    """
    res = []
    # Note that in the regex, {} is replaced by os.sep.
    regex = re.compile('^([+-])\W+({}.*)$'.format(re.escape(os.sep)))
    for line in f:
        line = line.rstrip()
        if line.startswith('#'):
            continue
        else:
            r = regex.match(line.rstrip())
            if not r:
                raise ValueError('Line "{}" is not a valid pattern.'.format(
                        line))
            modifier = r.groups()[0]
            pattern = r.groups()[1]
            # For directories, no trailing '/' is necessary according to our
            # pattern file format. In order to avoid confusion, we report an
            # error if we find a trailing '/'.
            if pattern != os.sep and pattern.endswith(os.sep):
                raise ValueError('Line "{}" is not a valid pattern.'.format(
                        line))
            if modifier == '+':
                res.append((INCLUDE, pattern))
            elif modifier == '-':
                res.append((EXCLUDE, pattern))
            else:
                raise ValueError('Unknown pattern modifier "{}".'.format(
                        modifier))
    return res


def path_matches_single_pattern(path, pattern):
    """Returns True iff path matches pattern.

    >>> path_matches_single_pattern('/foo/bar', '/foo')
    True

    >>> path_matches_single_pattern('/foobar', '/foo')
    False

    >>> path_matches_single_pattern('/foo', '/')
    True
    """
    if not (path.startswith(os.sep) and pattern.startswith(os.sep)):
        raise ValueError('Both file name ("{}") and pattern ("{}") must start with "{}".'.format(path, pattern, os.sep))

    norm_path = os.path.normpath(path)
    norm_pattern = os.path.normpath(pattern)

    if norm_path == norm_pattern:
        # if pattern is a path, then only the path itself can match
        return True
    elif norm_path.startswith(norm_pattern + os.sep):
        # if pattern is a subdirectory of root then path must
        # start with "pattern/"
        return True
    elif norm_pattern == os.sep:
        # if a pattern is root itself then any path matches
        return True
    else:
        # nothing else matches
        return False


def pattern_decision(path, patterns, default_decision=INCLUDE):
    res = default_decision
    for p in patterns:
        if path_matches_single_pattern(path, p[1]):
            res = p[0]
    return res


def assemble_paths(rootdir, patterns):
    filenames = []
    symlinks = []
    directories = []
    errors = []
    ignored = []

    def listdir_onerror(error):
        errors.append(error)

    rootdir = os.path.normpath(rootdir)

    # Handle root separately because the os.walk code below is not going to
    # process it.
    decision = pattern_decision(os.sep, patterns)
    if decision == INCLUDE:
        # If we want to include the directory entry, we have to find out
        # its type.
        if os.path.isdir(rootdir):
            directories.append(os.sep)
        else:
            raise ValueError('The root is not a directory, which should not happen.')
    elif decision != EXCLUDE:
        raise ValueError('Unknown file decision {}.'.format(decision))

    # Now recursively traverse the file system
    for root, dirs, files in os.walk(rootdir, topdown=True,
                                     onerror=listdir_onerror, followlinks=False):
        for f in itertools.chain(files, dirs):
            native_path = os.path.join(root, f)
            path = utils.get_path_from_native_path(rootdir, native_path)
            decision = pattern_decision(path, patterns)
            if decision == INCLUDE:
                # If we want to include the directory entry, we have to find out
                # its type.
                if os.path.islink(native_path):
                    symlinks.append(path)
                elif os.path.isfile(native_path):
                    filenames.append(path)
                elif os.path.isdir(native_path):
                    directories.append(path)
                else:
                    ignored.append(path)
            elif decision != EXCLUDE:
                raise ValueError('Unknown file decision {}.'.format(decision))
        # Also, we remove all mount points from dirs so that os.walk does not
        # recurse into a different file system.
        dirs[:] = [d for d in dirs if not os.path.ismount(os.path.join(rootdir, d))]

    return MatchingResult(filenames, symlinks, directories, errors, ignored)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    import StringIO
    import sys
    rootdir = sys.argv[1]
    if len(sys.argv) >= 3:
        patterns_file = open(sys.argv[2])
    else:
        patterns_file = StringIO.StringIO("# some test includes\n+ /\n")
    patterns = parse_pattern_file(patterns_file)
    res = assemble_paths(rootdir, patterns)

    print "The following files will be examined (relative to {}):".format(rootdir)
    for filename in res.filenames:
        print "{}".format(filename)

    print
    print "The following symlinks will be copied (relative to {}):".format(rootdir)
    for symlink in res.symlinks:
        print "{}".format(symlink)

    print
    print "The following directories will be copied (relative to {}):".format(rootdir)
    for directory in res.directories:
        print "{}".format(directory)

    print
    print "The following paths, although not excluded, were ignored:"
    for path in res.ignored:
        print "  {}".format(path)

    print
    print "The following errors were encountered:"
    for error in res.errors:
        print "  {}: {} (errno: {})".format(error.filename, error.strerror, error.errno)
