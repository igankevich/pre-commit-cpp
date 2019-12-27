import argparse
import chardet

def normalise_line_head(line, n):
    """Replace white-space characters at the beginning of the line with spaces"""
    if line.find('\t') == -1: return line
    result = ''
    white = True
    for c in line:
        if not c.isspace():
            result += c
            white = False
        elif white:
            if c == '\t': result += ' '*n # replace tabs with 4 spaces
            else: result += ' '           # replace other white-space characters with 1 space
        else: result += c
    print('Expand tabs')
    return result

def normalise_line_tail(line):
    """Replace white-space characters at the end of the line with a newline character"""
    l = line.rstrip() + '\n'
    if l != line: print('Remove trailing white-space')
    return l

def remove_empty_lines(lines):
    start = 0
    for i,line in enumerate(lines):
        start = i
        if line != '': break
    for i,line in enumerate(reversed(lines)):
        end = i
        if line != '': break
    end = len(lines) - end
    return lines[start:end]

def normalise_line(line, nspaces):
    return normalise_line_tail(normalise_line_head(line, nspaces))

def normalise_lines(lines):
    return remove_empty_lines(lines)

def remove_bom(content):
    if content[0:3] == b'\xef\xbb\xbf': content = content[:4]
    return content

def normalise_encoding(filename):
    ret = 0
    content = None
    with open(filename, 'rb') as f: content = f.read()
    c = remove_bom(content)
    if c != content:
        content = c
        ret = 1
        print('Remove BOM')
    encoding = chardet.detect(content)['encoding']
    if encoding != 'ascii' and encoding != 'utf-8':
        content = bytes(str(content, encoding), 'utf-8')
        ret = 1
        print('Convert from {} to utf-8'.format(encoding))
    if ret != 0:
        with open(filename, 'wb') as f: f.write(content);
    return ret

def int_positive(text):
    i = int(text)
    if i <= 0: raise argparse.ArgumentTypeError("%s must be positive" % text)
    return i

def main(argv=None):
    parser = argparse.ArgumentParser(description='Normalise C/C++ source code')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    parser.add_argument('--tab-width', help='Tab width', default=4, type=int_positive)
    args = parser.parse_args(argv)
    ret = 0
    for filename in args.filenames:
        ret = normalise_encoding(filename)
        lines = None
        with open(filename) as f:
            lines = f.readlines();
        for i,line in enumerate(lines):
            l = normalise_line(line, args.tab_width)
            if l != line:
                lines[i] = l
                ret = 1
        l = normalise_lines(lines)
        if len(l) != len(lines):
            lines = l
            ret = 1
        if ret != 0:
            with open(filename, 'w') as f:
                for line in lines:
                    f.write(line)
    return ret

if __name__ == '__main__':
    exit(main())

