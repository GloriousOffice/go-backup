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
        if f.startswith('#'):
            continue
        else:
            r = regex.match(line.rstrip())
            if not r:
                raise ValueError('Line "{}" is not a valid pattern.'.format(
                        line))
            if r.groups[0] == '+':
                res.append((INCLUDE, r.groups[1]))
            elif r.groups[0] == '-':
                res.append((EXCLUDE, r.groups[1]))
            else:
                raise ValueError('Unknown pattern modifier "{}".'.format(
                        r.groups[0]))
    return res

def filename_matches_pattern(filename, pattern):
    """Returns True iff filename matches pattern.

    >>> filename_matches_pattern('/foo/bar', '/foo')
    True

    >>> filename_matches_pattern('/foobar', '/foo')
    False
    """
    if not (filename.startswith(os.sep) and pattern.startswith(os.sep)):
        raise ValueError('Both file name ("{}") and pattern ("{}") must start with "{}".'.format(filename, pattern, os.sep))

    norm_filename = os.path.normpath(filename)
    norm_pattern = os.path.normpath(pattern)

    if norm_filename == norm_pattern:
        # if pattern is a file name, then only the file name itself can match
        return True
    elif norm_filename.startswith(norm_pattern + os.sep):
        # if pattern is a directory then file name must start with "pattern/"
        return True
    else:
        # nothing else matches
        return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()
