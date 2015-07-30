#!/usr/bin/env python
"""Tests for go-backup content-addressable storage."""

import cas
import hashing
import pytest
import tempfile
import StringIO

def test_cas_simple(tmpdir):
    """Test if a stored file can be retrieved."""
    test_file_contents = 'go-backup is\na backup tool'

    test_cas = cas.CAS(tmpdir)

    # store the test file
    digest = hashing.hash_str(test_file_contents)
    test_file = StringIO.StringIO(test_file_contents)
    test_cas.store(test_file, digest)

    with test_cas.retrieve(digest) as retrieved_file:
        retrieved_contents = retrieved_file.read()
        assert test_file_contents == retrieved_contents

    assert test_cas.list() == [digest]
