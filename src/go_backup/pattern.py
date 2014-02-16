import re

INCLUDE = 1
EXCLUDE = 2

def parse_pattern_file(f):
    res = []
    regex = re.compile('^([+-])\W+(.*)$')
    for line in f:
        line = line.rstrip()
        if f.startswith('#'):
            continue
        else
            r = regex.match(line.rstrip())
            if not r:
                raise ValueError('Line "{}" is not a valid pattern.'.format(
                        line))
            if r.groups[0] == '+':
                res.append((INCLUDE, r.groups[1]))
            elif r.groups[0] == '-':
                res.append((EXCLUDE, r.groups[1]))
            else:
                raise ValueError('Unknown pattern modifier "{}".'.format(
                        r.groups[0]))
    return res

def filename_matches_pattern(filename, pattern):


def filename_matches_patterns(filename, patterns):
    for p in patterns:
        
