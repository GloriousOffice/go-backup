import metadata
import pytest

def test_get_default_metadata_1(tmpdir):
    tmpfile = tmpdir.join("tmp.txt")
    tmpfile.write("test_content")

    res = metadata.get_default_metadata(str(tmpdir), '/tmp.txt')
    assert res['name'] == 'tmp.txt'
    # TODO: properly test these fields
    assert 'mtime' in res
    assert 'user' in res
    assert 'group' in res
    assert 'permissions' in res


def test_get_file_node_1(tmpdir):
    tmpfile = tmpdir.join("tmp.txt")
    tmpfile.write("test_content")

    hash_cache = {"/tmp.txt" : 'testhash1'}
    res = metadata.get_file_node(str(tmpdir), '/tmp.txt', hash_cache)
    assert isinstance(res, metadata.FileNode)
    assert res.name == 'tmp.txt'
    assert res.hash == 'testhash1'
    assert res.size == 12


def test_get_file_node_2(tmpdir):
    tmpfile = tmpdir.mkdir("test_dir").join("tmpfile.txt")
    tmpfile.write("abcde")

    hash_cache = {"/test_dir/tmpfile.txt" : 'hash0'}
    res = metadata.get_file_node(str(tmpdir), '/test_dir/tmpfile.txt', hash_cache)
    assert isinstance(res, metadata.FileNode)
    assert res.name == 'tmpfile.txt'
    assert res.hash == 'hash0'
    assert res.size == 5


def test_get_directory_node_1(tmpdir):
    testdir = tmpdir.mkdir("testdir")
    testfile1 = testdir.join("test1.txt")
    testfile2 = testdir.join("test2.txt")

    res = metadata.get_directory_node(str(tmpdir), '/testdir')
    assert isinstance(res, metadata.DirectoryNode)
    assert res.name == 'testdir'
    assert len(res.children) == 0


def test_get_symlink_node_1(tmpdir):
    tmpdir.join("testlink").mksymlinkto("test_destination")

    res = metadata.get_symlink_node(str(tmpdir), '/testlink')
    assert isinstance(res, metadata.SymlinkNode)
    assert res.link_target == 'test_destination'
