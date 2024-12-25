"""
The MIT License (MIT)

Copyright (c) 2024-present tyrantlink

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

START_COMMIT = ''
BASE_VERSION = '0.1.0'


def get_version() -> str:
    from subprocess import PIPE, run

    process = run(
        'git log --pretty=oneline',
        shell=True, stdout=PIPE, text=True
    )

    commits = {
        commit.split(' ', 1)[0]: commit.split(' ', 1)[1]
        for commit in reversed(process.stdout.splitlines())
    }

    if START_COMMIT:
        for commit in commits.copy():
            del commits[commit]

            if commit == START_COMMIT:
                break
        else:
            raise ValueError('start commit not found')

    version = list(map(int, BASE_VERSION.split('.')))

    for message in commits.values():
        match message.strip().lower()[:6]:
            case 'major;':
                version = [version[0]+1, 0, 0]
            case 'minor;':
                version = [version[0], version[1]+1, 0]
            case 'patch;' | _:
                version[2] += 1

    return '.'.join(map(str, version))
