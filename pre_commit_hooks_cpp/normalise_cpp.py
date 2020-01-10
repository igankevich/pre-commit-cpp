import argparse
import re
import os

INCLUDE_RELATIVE = re.compile(r'\s*#include\s+"([^"]+)"\s*\n')
INCLUDE_SYSTEM = re.compile(r'\s*#include\s+<([^>]+)>\s*\n')

def relativise_include_path(source_filename, line, src, line_no):
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
                print('{}:{}:1 fix include path'.format(source_filename, line_no))
    return line

def sort_include_paths(lines, top_headers):
    # expand header names
    for i,name in enumerate(top_headers):
        top_headers[i] = '#include <{}>\n'.format(name)
    result = []
    block = []
    for i,line in enumerate(lines):
        m = INCLUDE_SYSTEM.match(line)
        if m:
            line = line.lstrip()
            block.append(line)
        else:
            if len(block) > 0:
                offset = 0
                for include in top_headers:
                    try:
                        idx = block.index(include)
                        block[idx], block[offset] = block[offset], block[idx]
                        offset += 1
                    except:
                        pass
                block[offset:] = sorted(set(block[offset:]))
                result.extend(block)
                block = []
            result.append(line)
    return result

def normalise_include_statements(filename, args):
    ret = 0
    lines = None
    with open(filename) as f:
        lines = f.readlines();
    for i,line in enumerate(lines):
        l = relativise_include_path(filename, line, args.src, i)
        if l != line:
            lines[i] = l
            ret = 1
    new_lines = sort_include_paths(lines, args.top)
    if new_lines != lines:
        lines = new_lines
        ret = 1
    if ret != 0:
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)
    return ret

def main(argv=None):
    parser = argparse.ArgumentParser(description='Normalise C/C++ source code')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    parser.add_argument('--src', help='Source directory relative to which include filenames are expanded', default='src')
    parser.add_argument('--top', nargs='+', help='Headers that must be at the top of the list', default=['sys/types.h'])
    args = parser.parse_args(argv)
    args.src = os.path.abspath(args.src)
    ret = 0
    for filename in args.filenames:
        ret |= normalise_include_statements(filename, args)
    return ret

if __name__ == '__main__':
    exit(main())

