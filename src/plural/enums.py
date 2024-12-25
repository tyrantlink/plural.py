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
from enum import Enum, IntFlag


class Intents(IntFlag):
    NONE = 0
    MEMBERS_READ = 1 << 0
    MEMBERS_WRITE = 1 << 1
    MEMBERS_EVENTS = 1 << 2
    GROUPS_READ = 1 << 3
    GROUPS_WRITE = 1 << 4
    GROUPS_EVENTS = 1 << 5
    LATCH_READ = 1 << 6
    LATCH_WRITE = 1 << 7
    LATCH_EVENTS = 1 << 8
    MESSAGES_WRITE = 1 << 9
    MESSAGES_EVENTS = 1 << 10
    MEMBERS_USERPROXY_TOKEN_READ = 1 << 11
    MEMBERS_USERPROXY_TOKEN_WRITE = 1 << 12
    GROUPS_SHARE = 1 << 13


class ImageExtension(Enum):
    PNG = 0
    JPG = 1
    JPEG = 1  # noqa: PIE796
    GIF = 2
    WEBP = 3

    @property
    def mime_type(self) -> str:
        return {
            ImageExtension.PNG: 'image/png',
            ImageExtension.JPG: 'image/jpeg',
            ImageExtension.GIF: 'image/gif',
            ImageExtension.WEBP: 'image/webp'
        }[self]
