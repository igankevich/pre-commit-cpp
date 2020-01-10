import argparse
import re
import os
from enum import IntEnum

INCLUDE_RELATIVE = re.compile(r'\s*#include\s+"([^"]+)"\s*\n')
INCLUDE_SYSTEM = re.compile(r'\s*#include\s+<([^>]+)>\s*\n')
STRAY_BRACE = re.compile(r'^\s*[\)\}\]>]+\s*;*\s*\n')

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

class Token(IntEnum):
    Brace = 0,   # {}
    Bracket = 1, # []
    Paren = 2,   # ()
    Angle = 3,   # <>

def normalise_indent(filename, args):
    ret = 0
    lines = None
    with open(filename) as f:
        lines = f.readlines();
    level = 0
    new_lines = []
    tokens = [0]*len(Token)
    multiline_comment = False
    inside_string = False
    inside_char = False
    for i,line in enumerate(lines):
        new_level = level
        min_level = 100
        if not line.lstrip().startswith('//'):
            c0 = ' '
            c1 = ' '
            multiline_comment_line = multiline_comment
            for c in line:
                if inside_string:
                    if (c0 != '\\' or c1 == '\\') and c == '"': inside_string = False;
                elif inside_char:
                    if (c0 != '\\' or c1 == '\\') and c == '\'': inside_char = False;
                elif multiline_comment:
                    if c0 == '*' and c == '/':
                        multiline_comment = False
                        multiline_comment_line = False
                else:
                    if c == '{': tokens[Token.Brace] += 1
                    elif c == '}': tokens[Token.Brace] -= 1
                    elif c == '[': tokens[Token.Bracket] += 1
                    elif c == ']': tokens[Token.Bracket] -= 1
                    elif c == '(': tokens[Token.Paren] += 1
                    elif c == ')': tokens[Token.Paren] -= 1
                    elif c == '<': tokens[Token.Angle] += 1
                    elif c == '>' and (c0 != '-' or c1 == '-'): tokens[Token.Angle] -= 1
                    elif c0 == '/' and c == '*': multiline_comment = True
                    elif c == '"': inside_string = True
                    elif c == '\'': inside_char = True
                c1 = c0
                c0 = c
                new_level = sum(tokens)
                min_level = min(new_level,min_level)
        if min_level < level and new_level >= level: level = min_level
        if new_level < level and STRAY_BRACE.match(line): level = new_level
        #if new_level < level: level = new_level
        if multiline_comment_line:
            new_lines.append(line)
        else:
            if line != '\n': line = line.lstrip()
            new_lines.append((' '*level*args.tab_width) + line)
        level = new_level
    if new_lines != lines:
        lines = new_lines
        ret = 1
    if ret != 0:
        with open(filename, 'w') as f:
            for line in lines:
                f.write(line)
    return ret

def int_positive(text):
    i = int(text)
    if i <= 0: raise argparse.ArgumentTypeError("%s must be positive" % text)
    return i

def main(argv=None):
    parser = argparse.ArgumentParser(description='Normalise C/C++ source code')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    parser.add_argument('--src', help='Source directory relative to which include filenames are expanded', default='src')
    parser.add_argument('--top', nargs='+', help='Headers that must be at the top of the list', default=['sys/types.h'])
    parser.add_argument('--tab-width', help='Tab width', default=4, type=int_positive)
    args = parser.parse_args(argv)
    args.src = os.path.abspath(args.src)
    ret = 0
    for filename in args.filenames:
        ret |= normalise_include_statements(filename, args)
        #ret |= normalise_indent(filename, args)
    return ret

if __name__ == '__main__':
    exit(main())

