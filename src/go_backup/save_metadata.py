#!/usr/bin/env python

import hashdeep
import metadata
import os.path
import pattern
import sys

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "usage: %s rootdir patterns_file metadata_file" % sys.argv[0]
        sys.exit(1)

    rootdir = os.path.normpath(sys.argv[1])

    patterns_file = open(sys.argv[2])
    patterns = pattern.parse_pattern_file(patterns_file)
    pathlist = pattern.assemble_paths(rootdir, patterns)

    digests = hashdeep.compute_digests(rootdir, pathlist.filenames)
    backup_metadata = metadata.get_backup_metadata(rootdir=rootdir,
                                                   files=pathlist.filenames,
                                                   symlinks=pathlist.symlinks,
                                                   directories=pathlist.directories,
                                                   digest_map=digests)

    with open(sys.argv[3], "w") as metadata_file:
        metadata.write_backup_metadata(metadata_file, backup_metadata)
