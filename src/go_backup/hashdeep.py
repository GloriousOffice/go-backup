#!/usr/bin/env python

import xml.etree.ElementTree as ET
import os
import subprocess
import tempfile
from collections import namedtuple

import utils

Digest = namedtuple('Digest', ['sha1', 'sha256'])

def version():
    try:
        v = subprocess.check_output(['hashdeep', '-V'])
        return v.strip()
    except:
        return None


def is_supported_version(version):
    supported_versions = ['4.2', '4.3', '4.4']
    return version in supported_versions


def compute_digests(rootdir, paths, num_threads=None):
    """Return a dict with (path, digest)."""

    # First, we write the temporary file with filenames in the format
    # expected by hashdeep
    rootdir = os.path.normpath(rootdir)
    fd, tempfilename = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmpfile:
        for p in paths:
            tmpfile.write(utils.build_native_path(rootdir, p))
            tmpfile.write('\n')

    # Run hashdeep -c sha1,sha256 -f tempfilename -l -d (-j num_threads)
    cmd = ['hashdeep', '-c', 'sha1,sha256', '-f', tempfilename, '-l', '-d']
    if num_threads is not None:
        cmd.extend(['-j', str(num_threads)])
    output = subprocess.check_output(cmd)

    # Delete temporary file
    os.remove(tempfilename)
  
    # Parse output
    root = ET.fromstring(output)
    res = {}

    for fileobj in root:
        if fileobj.tag != 'fileobject':
            continue

        name = None
        sha1 = None
        sha256 = None
        for child in fileobj:
            if child.tag == 'hashdigest':
                if child.attrib['type'] == 'SHA1':
                    sha1 = child.text
                elif child.attrib['type'] == 'SHA256':
                    sha256 = child.text
                else:
                    raise ValueError('Unexpected hash type "{}".'.format(
                        child.attrib['type']))
            if child.tag == 'filename':
                name = utils.get_path_from_native_path(rootdir, child.text)
        if not name or not sha1 or not sha256:
            raise ValueError('Could not extract all required information from '
                'digest.')
        res[name] = Digest(sha1, sha256)

    keys = res.keys()
    if len(keys) != len(paths) or set(keys) != set(paths):
        raise ValueError('List of filenames returned by hashdeep does not '
            'match the input list.')
    
    return res


if __name__ == "__main__":
    import sys
    v = version()
    supp = is_supported_version(v)
    print 'hashdeep version: {}  (compatible: {})'.format(v, supp)
    if len(sys.argv) == 3:
        rootdir = sys.argv[1]
        filename_file = sys.argv[2]
        filenames = []
        with open(filename_file) as tmpfile:
            for line in tmpfile:
                filenames.append(line.strip())
        result = compute_digests(rootdir, filenames)
        print result
