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


def pattern_decision(filename, patterns, default_decision=INCLUDE):
    res = default_decision
    for p in patterns:
        if filename_matches_single_pattern(filename, p[1]):
            res = p[0]
    return res

def listdir_onerror(error):
    raise error

def assemble_filenames(rootdir, patterns):
    res = []
    for root, dirs, files in os.walk(rootdir, topdown=True,
            onerror=listdir_onerror, followlinks=False)
        for f in files:
            filename = os.path.join(root, f)
            # The "root" returned by os.walk includes rootdir. We strip out this
            # part so that the filename starts with os.sep.
            filename = 
            decision = pattern_decision(filename, patterns)
            if decision == INCLUDE:
                res.append(filename)
            elif decision != EXCLUDE:
                raise ValueError('Unknown file decision {}.'.format(decision))
    return res
