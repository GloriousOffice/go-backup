#!/usr/bin/env python
"""Tests for go-backup hashing module.

Test vectors here are taken from NIST's NSRL Test Data page
http://www.nsrl.nist.gov/testdata/.
"""

import hashing
import pytest
import StringIO

abc = "abc"
abc_digest = "BA7816BF 8F01CFEA 414140DE 5DAE2223 B00361A3 96177A9C B410FF61 F20015AD"

abc2 = "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"
abc2_digest = "248D6A61 D20638B8 E5C02693 0C3E6039 A33CE459 64FF2167 F6ECEDD4 19DB06C1"

million_a = "a" * 1000 * 1000
million_a_digest ="CDC76E5C 9914FB92 81A1C7E2 84D73E67 F1809A48 A497200E 046D39CC C7112CD0"

def NIST_digest_to_hexdigest(s):
    """Convert and return digest from its verbatim form on NSRL Test Data page to the
    form returned by hexdigest() methods."""
    return s.lower().replace(" ", "")

abc_digest = NIST_digest_to_hexdigest(abc_digest)
abc2_digest = NIST_digest_to_hexdigest(abc2_digest)
million_a_digest = NIST_digest_to_hexdigest(million_a_digest)

def test_hash_str_1():
    assert hashing.hash_str(abc) == abc_digest

def test_hash_str_2():
    assert hashing.hash_str(abc2) == abc2_digest

def test_hash_fileobj_1():
    fileobj = StringIO.StringIO(million_a)
    assert hashing.hash_fileobj(fileobj) == million_a_digest

def test_hash_fileobj_2(tmpdir):
    test_fn = str(tmpdir.join("million_a.txt"))

    # create a file with million a's in it
    with open(test_fn, "wb") as test_file:
        for i in xrange(1000):
            test_file.write(1000 * "a")

    # check its hash
    with open(test_fn, "rb") as test_file:
        assert hashing.hash_fileobj(test_file) == million_a_digest
