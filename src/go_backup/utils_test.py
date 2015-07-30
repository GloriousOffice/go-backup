import utils
import pytest
import pwd
import grp

def test_build_native_path_simple_1():
    rootdir = '/home/x'
    path = '/foo'
    res = utils.build_native_path(rootdir, path)
    assert res == '/home/x/foo'

def test_build_native_path_simple_2():
    rootdir = '/home/x'
    path = '/foo/bar'
    res = utils.build_native_path(rootdir, path)
    assert res == '/home/x/foo/bar'

def test_build_native_path_simple_base_path():
    rootdir = '/home/x'
    path = '/'
    res = utils.build_native_path(rootdir, path)
    assert res == '/home/x'

def test_build_native_path_simple_base_rootdir_some_path():
    rootdir = '/'
    path = '/foo/bar'
    res = utils.build_native_path(rootdir, path)
    assert res == '/foo/bar'

def test_build_native_path_simple_base_rootdir_base_path():
    rootdir = '/'
    path = '/'
    res = utils.build_native_path(rootdir, path)
    assert res == '/'

def test_build_native_path_non_absolute_rootdir():
    rootdir = 'root'
    path = '/'
    with pytest.raises(ValueError):
        res = utils.build_native_path(rootdir, path)

def test_build_native_path_non_normalized_rootdir():
    rootdir = '/home//x'
    path = '/'
    with pytest.raises(ValueError):
        res = utils.build_native_path(rootdir, path)

def test_build_native_path_non_normalized_path():
    rootdir = '/home/x'
    path = '/foo/../bar'
    with pytest.raises(ValueError):
        res = utils.build_native_path(rootdir, path)

def test_get_path_from_native_path_simple_1():
    rootdir = '/home/x'
    native_path = '/home/x/foo'
    res = utils.get_path_from_native_path(rootdir, native_path)
    assert res == '/foo'

def test_get_path_from_native_path_simple_2():
    rootdir = '/foo'
    native_path = '/foo/bar/baz'
    res = utils.get_path_from_native_path(rootdir, native_path)
    assert res == '/bar/baz'

def test_get_path_from_native_path_base_rootdir():
    rootdir = '/'
    native_path = '/foo/bar'
    res = utils.get_path_from_native_path(rootdir, native_path)
    assert res == '/foo/bar'

def test_get_path_from_native_path_both_dirs_base():
    rootdir = '/'
    native_path = '/'
    res = utils.get_path_from_native_path(rootdir, native_path)
    assert res == '/'

def test_get_path_from_native_path_equal_paths():
    rootdir = '/home/x'
    native_path = '/home/x'
    res = utils.get_path_from_native_path(rootdir, native_path)
    assert res == '/'

def test_get_path_from_native_path_non_absolute_rootdir():
    rootdir = 'foo'
    native_path = '/foo'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_from_native_path_non_absolute_native_path():
    rootdir = '/'
    native_path = 'foo'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_from_native_path_non_normalized_rootdir():
    rootdir = '//foo'
    native_path = '/foo'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_from_native_path_non_normalized_native_path():
    rootdir = '/'
    native_path = '/foo/../bar'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_from_native_path_out_of_dir_path_1():
    rootdir = '/foo'
    native_path = '/'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_from_native_path_out_of_dir_path_1():
    rootdir = '/foo/bar'
    native_path = '/foobar'
    with pytest.raises(ValueError):
        res = utils.get_path_from_native_path(rootdir, native_path)

def test_get_path_parts_1():
    path = '/foo/bar/baz'
    res = utils.get_path_parts(path)
    assert list(res) == ['foo', 'bar', 'baz']

def test_get_path_parts_2():
    path = '/foo/bar/baz/'
    with pytest.raises(ValueError):
        res = utils.get_path_parts(path)

def test_get_path_parts_3():
    path = '/'
    res = utils.get_path_parts(path)
    assert list(res) == []

def test_get_path_parts_4():
    path = '/abc'
    res = utils.get_path_parts(path)
    assert list(res) == ['abc']

def test_get_uid_name_map_consistency():
    # TODO: maybe mock out in future?
    uid_name_map = utils.get_uid_name_map()
    for (uid, name) in uid_name_map.iteritems():
        assert pwd.getpwuid(uid).pw_name == name
        assert pwd.getpwnam(name).pw_uid == uid

def test_get_gid_name_map_consistency():
    # TODO: maybe mock out in future?
    gid_name_map = utils.get_gid_name_map()
    for (gid, name) in gid_name_map.iteritems():
        assert grp.getgrgid(gid).gr_name == name
        assert grp.getgrnam(name).gr_gid == gid

def test_filemode_simple_1():
    mode = 0o644
    res = utils.filemode(mode)
    assert res == '-rw-r--r--'

def test_filemode_simple_2():
    mode = 0o741
    res = utils.filemode(mode)
    assert res == '-rwxr----x'

def test_filemode_sticky():
    mode = 0o1700
    res = utils.filemode(mode)
    assert res == '-rwx-----T'

def test_filemode_setuid_1():
    mode = 0o4700
    res = utils.filemode(mode)
    assert res == '-rws------'

def test_filemode_setuid_2():
    mode = 0o4600
    res = utils.filemode(mode)
    assert res == '-rwS------'
