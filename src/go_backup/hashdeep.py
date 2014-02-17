#!/usr/bin/env python

import xml.etree.ElementTree as ET
import os
import subprocess
import tempfile
from collections import namedtuple

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


# Return a dict with (filename, digest)
def compute_digests(rootdir, filenames, num_threads=-1):
    # First, we write the temporary file with filenames in the format expected
    # by hashdeep
    rootdir = os.path.normpath(rootdir)
    fd, tempfilename = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmpfile:
        for f in filenames:
            if rootdir != os.sep:
                if f.startswith(os.sep):
                  f = f[len(os.sep):]
                f = os.path.join(rootdir, f)
            tmpfile.write(f)
            tmpfile.write('\n')
          
    # Run hashdeep -c sha1,sha256 -f tempfilename -l -d (-j num_threads)
    cmd = ['hashdeep', '-c', 'sha1,sha256', '-f', tempfilename, '-l', '-d']
    if num_threads > -1:
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
                name = child.text
                if rootdir != os.sep:
                    name = name[len(rootdir):]
        if not name or not sha1 or not sha256:
            raise ValueError('Could not extract all required information from '
                'digest.')
        res[name] = Digest(sha1, sha256)

    keys = res.keys()
    if len(keys) != len(filenames) or set(keys) != set(filenames):
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
