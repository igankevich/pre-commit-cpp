import argparse
import subprocess
from enum import IntEnum

GPL3_LICENSE_NOTICE = """This file is part of {0}.

{0} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

{0} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with {0}.  If not, see <https://www.gnu.org/licenses/>."""

UNLICENSE_NOTICE = """This file is part of {0}.

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>"""

class State(IntEnum):
    Initial = 0,
    Start = 1,
    Found = 2,

def copyright_notice(filename, aliases, args):
    result = subprocess.run(
        ['git', '--no-pager', 'log', '--pretty=format:%an|%ad', '--date=format:%Y',
            '--follow', '--', filename],
        stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    if not result: return args.copyright_string
    authors = {}
    for line in result.split('\n'):
        pair = line.split('|')
        print(pair)
        author = aliases.get(pair[0], pair[0])
        date = pair[1]
        dates = authors.get(author, [])
        dates.append(date)
        authors[author] = sorted(set(dates))
    lines = []
    for author,dates in authors.items():
        lines.append(args.copyright_string + ' ' + ', '.join(dates) + ' ' + author)
    return '\n'.join(sorted(lines))

def full_notice(filename, aliases, args):
    result = ''
    result += '/*'
    if args.preamble:
        result += '\n'
        result += args.preamble
    result += '\n'
    result += copyright_notice(filename, aliases, args)
    result += '\n\n'
    result += args.license_notice.format(args.programme_name)
    if args.postamble:
        result += '\n'
        result += args.postamble
    result += '\n'
    result += '*/'
    return result

def add_comment(content, filename, aliases, args):
    position = 0
    length = len(content)
    state = State.Initial
    start = 0
    end = 0
    while position != length:
        if state == State.Initial:
            idx = content.find('/*', position)
            if idx != -1:
                state = State.Start
                position = idx
                start = idx
            else:
                position = length
        elif state == State.Start:
            idx1 = content.find(args.copyright_string, position)
            idx2 = content.find('*/', position)
            if idx1 != -1 and idx2 != -1 and idx1 < idx2:
                state = State.Found
                end = idx2 + 2
                position = length
            elif idx1 != -1 and idx2 != -1:
                state = State.Initial
                position = min(idx1, idx2)
            elif idx1 != -1 and idx2 == -1:
                state = State.Initial
                position = idx1
            elif idx1 == -1 and idx2 != -1:
                state = State.Initial
                position = idx2
            else:
                state = State.Initial
                position = length
    if state == State.Found:
        content = content[:start] + full_notice(filename, aliases, args) + content[end:]
    else:
        content = full_notice(filename, aliases, args) + '\n\n' + content
    return content

def main(argv=None):
    parser = argparse.ArgumentParser(description='Prepend/update copyright and license notices')
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    parser.add_argument('--copyright-string', help='Copyright string that must be present in the comment', default='Copyright ©')
    parser.add_argument('--programme-name', help='Name of the programme', default='Foobar')
    parser.add_argument('--preamble', help='Comment preamble', default='')
    parser.add_argument('--license-notice', help='License notice text', default='gpl3+')
    parser.add_argument('--postamble', help='Comment postamble', default='')
    parser.add_argument('--alias', nargs='+', help='Define author alias', default=[])
    args = parser.parse_args(argv)
    if args.license_notice == 'gpl3+': args.license_notice = GPL3_LICENSE_NOTICE
    elif args.license_notice == 'unlicense': args.license_notice = UNLICENSE_NOTICE
    aliases = {}
    for alias in args.alias:
        pair = alias.split(':')
        aliases[pair[0]] = pair[1]
    ret = 0
    for filename in args.filenames:
        content = None
        with open(filename) as f:
            content = f.read();
        new_content = add_comment(content, filename, aliases, args)
        if new_content != content:
            content = new_content
            ret = 1
        if ret != 0:
            print('{}: update copyright/license notice'.format(filename))
            with open(filename, 'w') as f:
                f.write(content)
    return ret

if __name__ == '__main__':
    exit(main())


