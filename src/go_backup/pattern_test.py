import pattern
import pytest
import StringIO

I = pattern.INCLUDE
E = pattern.EXCLUDE

def parse_pattern_file_wrapper(s):
    return pattern.parse_pattern_file(StringIO.StringIO(s))

def test_parse_pattern_file_simple_1():
    s = '- /foo\n- /bar\n+ /foo/go'
    res = parse_pattern_file_wrapper(s)
    assert len(res) == 3
    assert res[0] == (E, '/foo')
    assert res[1] == (E, '/bar')
    assert res[2] == (I, '/foo/go')

def test_parse_pattern_file_simple_2():
    s = '- /\n+ /bar\n+ / foo'
    res = parse_pattern_file_wrapper(s)
    assert len(res) == 3
    assert res[0] == (E, '/')
    assert res[1] == (I, '/bar')
    assert res[2] == (I, '/ foo')

def test_parse_pattern_file_initial_space():
    s = '-/\n+ /foo'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_pattern_modifier():
    s = '- /\n* /foo'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_unnormalized_pattern_1():
    s = '- /\n+ /foo/'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_unnormalized_pattern_2():
    s = '- /\n+ /foo/.'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_unnormalized_pattern_3():
    s = '- /\n+ /foo//bar'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_unnormalized_pattern_4():
    s = '- /\n+ /foo/../bar'
    with pytest.raises(ValueError):
        parse_pattern_file_wrapper(s)

def test_parse_pattern_file_nonstandard_space():
    s = '-  /bar\n+\t/foo'
    res = parse_pattern_file_wrapper(s)
    assert len(res) == 2
    assert res[0] == (E, '/bar')
    assert res[1] == (I, '/foo')


def pmsp_wrapper(a, b):
    return pattern.path_matches_single_pattern(a, b)

def test_path_matches_single_path_simple_1():
    assert pmsp_wrapper('/foo/bar', '/foo')

def test_path_matches_single_path_simple_2():
    assert not pmsp_wrapper('/foobar', '/foo')

def test_path_matches_single_path_simple_3():
    assert pmsp_wrapper('/foo', '/')

def test_path_matches_single_path_simple_4():
    assert not pmsp_wrapper('/foo', '/bar')

def test_path_matches_single_path_check_input_1():
    with pytest.raises(ValueError):
        pmsp_wrapper('foo', '/bar')

def test_path_matches_single_path_check_input_2():
    with pytest.raises(ValueError):
        pmsp_wrapper('/foo', 'bar')

def test_path_matches_single_path_check_input_3():
    with pytest.raises(ValueError):
        pmsp_wrapper('foo', 'bar')

def test_path_matches_single_path_check_input_4():
    with pytest.raises(ValueError):
        pmsp_wrapper('/baz/../baz', '/baz')

def test_path_matches_single_path_check_input_5():
    with pytest.raises(ValueError):
        pmsp_wrapper('/baz/xyz', '/baz/')

def test_path_matches_single_path_check_input_6():
    with pytest.raises(ValueError):
        pmsp_wrapper('/a/.', '/b')

def test_path_matches_single_path_check_input_7():
    with pytest.raises(ValueError):
        pmsp_wrapper('/x//y', '/x')

def test_path_matches_single_path_long_1():
    assert pmsp_wrapper('/xyz/foo/bar', '/xyz/foo')

def test_path_matches_single_path_long_2():
    assert not pmsp_wrapper('/xyz/fo/bar', '/xyz/foo')

def test_path_matches_single_path_long_3():
    assert pmsp_wrapper('/xyz/foo/bar/baz/foo/bar/foo', '/')

def test_path_matches_single_path_long_4():
    assert not pmsp_wrapper('/xyz/foo/bar/baz/foo/bar/foo', '/foo')

def test_path_matches_single_path_long_5():
    assert pmsp_wrapper('/xyz/foo/bar/baz/foo/bar/foo',
                        '/xyz/foo/bar/baz/foo/bar/foo')

def test_path_matches_single_path_long_6():
    assert not pmsp_wrapper('/xyz/foo/bar/baz/foo/bar/foo', '/baz')


def pd_wrapper(a, b):
    v = pattern.pattern_decision(a, b)
    assert v == I or v == E
    return v == I

def test_pattern_decision_simple_1():
    assert pd_wrapper('/foo', [])

def test_pattern_decision_simple_2():
    assert pd_wrapper('/foo', [(E, '/'), (I, '/foo'), (E, '/fo')])

def test_pattern_decision_simple_3():
    assert not pd_wrapper('/fo', [(E, '/'), (I, '/foo'), (E, '/fo')])

def test_pattern_decision_simple_4():
    assert pd_wrapper('/foo/bar', [(E, '/'), (I, '/foo'), (E, '/fo')])

def test_pattern_decision_simple_5():
    assert not pd_wrapper('/foo', [(E, '/'), (I, '/foo/bar'), (E, '/fo')])
