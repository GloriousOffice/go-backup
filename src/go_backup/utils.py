#!/usr/bin/env python
import os.path

def build_native_path(rootdir, path):
    """Returns a native path obtained by concatenating rootdir with a
    path that's absolute in the chdir of that rootdir.

    >>> build_native_path('/home/x', '/foo')
    '/home/x/foo'

    >>> build_native_path('/home/x', '/foo/bar')
    '/home/x/foo/bar'

    >>> build_native_path('/', '/foo/bar')
    '/foo/bar'

    >>> build_native_path('/', '/')
    '/'
    """
    if path.startswith(os.sep):
        path = path[len(os.sep):]
    return os.path.join(rootdir, path)

def get_path_from_native_path(rootdir, native_path):
    """Returns a path given a native path.

    >>> get_path_from_native_path('/home/x', '/home/x/foo')
    '/foo'

    >>> get_path_from_native_path('/home/x', '/home/x/foo/bar')
    '/foo/bar'

    >>> get_path_from_native_path('/', '/foo/bar')
    '/foo/bar'

    >>> get_path_from_native_path('/', '/')
    '/'
    """
    if rootdir == os.sep:
        return native_path
    elif native_path.startswith(rootdir + os.sep):
        return native_path[len(rootdir):]
    else:
        raise ValueError('Native path {} is not a valid path for root directory {}.'.format(rootdir, native_path))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
