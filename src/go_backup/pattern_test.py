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

def test_parse_pattern_file_trailing_slash():
  s = '- /\n+ /foo/'
  with pytest.raises(ValueError):
    parse_pattern_file_wrapper(s)

def test_parse_pattern_file_nonstandard_space():
  s = '-  /bar\n+\t/foo'
  res = parse_pattern_file_wrapper(s)
  assert len(res) == 2
  assert res[0] == (E, '/bar')
  assert res[1] == (I, '/foo')
