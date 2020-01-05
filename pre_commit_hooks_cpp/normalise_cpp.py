import argparse
import re
import os

INCLUDE_RELATIVE = re.compile(r'\s*#include\s+"([^"]+)"\s*\n')

def normalise_include_path(source_filename, line, src):
    from os.path import isfile, join
    dir = os.path.dirname(source_filename)
    m = INCLUDE_RELATIVE.match(line)
    if m:
        filename = m.group(1)
        filename = os.path.abspath(join(dir, filename))
        prefix = os.path.commonprefix([filename,src])
        if prefix == src:
            filename = os.path.relpath(filename, src)
            filename = os.path.normcase(filename).replace('\\','/')
            filename_win = filename.lower()
            # fix windows paths
            if filename_win != filename and \
               not isfile(join(src,filename)) and \
               isfile(join(src,filename_win)):
                filename = filename_win
            if isfile(join(src,filename)):
                line = '#include <{}>\n'.format(filename)
    return line

def normalise_include_statements(filename, args):
    args.src = os.path.abspath(args.src)
    ret = 0
    lines = None
    with open(filename) as f:
        lines = f.readlines();
    for i,line in enumerate(lines):
        l = normalise_include_path(filename, line, args.src)
        if l != line:
            lines[i] = l
            ret = 1
    if ret != 0:
        print('fix include paths')
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)
    return ret

def main(argv=None):
    parser = argparse.ArgumentParser(description='Normalise C/C++ source code')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    parser.add_argument('--src', help='Source directory relative to which include filenames are expanded', default='src')
    args = parser.parse_args(argv)
    args.src = os.path.abspath(args.src)
    ret = 0
    for filename in args.filenames:
        ret |= normalise_include_statements(filename, args)
    return ret

if __name__ == '__main__':
    exit(main())

