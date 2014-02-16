#!/usr/bin/env python
import os
import re

INCLUDE = 1
EXCLUDE = 2

def parse_pattern_file(f):
    res = []
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
            if r.groups()[0] == '+':
                res.append((INCLUDE, r.groups()[1]))
            elif r.groups()[0] == '-':
                res.append((EXCLUDE, r.groups()[1]))
            else:
                raise ValueError('Unknown pattern modifier "{}".'.format(
                        r.groups()[0]))
    return res

def filename_matches_single_pattern(filename, pattern):
    """Returns True iff filename matches pattern.

    >>> filename_matches_single_pattern('/foo/bar', '/foo')
    True

    >>> filename_matches_single_pattern('/foobar', '/foo')
    False

    >>> filename_matches_single_pattern('/foo', '/')
    True
    """
    if not (filename.startswith(os.sep) and pattern.startswith(os.sep)):
        raise ValueError('Both file name ("{}") and pattern ("{}") must start with "{}".'.format(filename, pattern, os.sep))

    norm_filename = os.path.normpath(filename)
    norm_pattern = os.path.normpath(pattern)

    if norm_filename == norm_pattern:
        # if pattern is a file name, then only the file name itself can match
        return True
    elif norm_filename.startswith(norm_pattern + os.sep):
        # if pattern is a subdirectory of root then file name must
        # start with "pattern/"
        return True
    elif norm_pattern == os.sep:
        # if a pattern is root itself then any filename matches
        return True
    else:
        # nothing else matches
        return False


def pattern_decision(filename, patterns, default_decision=INCLUDE):
    res = default_decision
    for p in patterns:
        if filename_matches_single_pattern(filename, p[1]):
            res = p[0]
    return res

def assemble_filenames(rootdir, patterns):
    filenames = []
    errors = []

    def listdir_onerror(error):
        errors.append(error)

    rootdir = os.path.normpath(rootdir)
    for root, dirs, files in os.walk(rootdir, topdown=True,
                                     onerror=listdir_onerror, followlinks=False):
        for f in files:
            filename = os.path.join(root, f)
            # The "root" returned by os.walk includes rootdir. We strip out this
            # part so that the filename starts with os.sep. Note that we have
            # a special case of rootdir is os.sep because in that case, normpath
            # does not remove the trailing os.sep.
            if rootdir != os.sep:
              filename = filename[len(rootdir):]
            decision = pattern_decision(filename, patterns)
            if decision == INCLUDE:
                filenames.append(filename)
            elif decision != EXCLUDE:
                raise ValueError('Unknown file decision {}.'.format(decision))
    return (filenames, errors)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    import StringIO
    import sys
    rootdir = sys.argv[1]
    test_includes = StringIO.StringIO("# some test includes\n+ /\n")
    patterns = parse_pattern_file(test_includes)
    filenames, errors = assemble_filenames(rootdir, patterns)

    print "The following files will be examined (relative to {}):".format(rootdir)
    for filename in filenames:
        print "{}".format(filename)

    print
    print "The following errors were encountered:"
    for error in errors:
        print "  {}: {} (errno: {})".format(error.filename, error.strerror, error.errno)
    # TODO: permission denied
