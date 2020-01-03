import argparse
import re

KEYWORD = r'\b__(global|local|constant|private|generic|kernel|read_only|write_only|read_write)\b'

def main(argv=None):
    parser = argparse.ArgumentParser(description='Normalise OpenCL keywords')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    args = parser.parse_args(argv)
    ret = 0
    for filename in args.filenames:
        content = None
        with open(filename) as f:
            content = f.read();
        new_content = re.sub(KEYWORD, r'\1', content)
        if new_content != content:
            content = new_content
            ret = 1
        if ret != 0:
            with open(filename, 'w') as f:
                f.write(content)
    return ret

if __name__ == '__main__':
    exit(main())

