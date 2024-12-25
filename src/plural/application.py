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
from typing import overload, Literal, Any

from aiohttp import ClientSession

from .http import request, Route
from .models import Message
from .enums import Intents
from .user import User


class Application:
    __session: ClientSession | None = None

    def __init__(self, token: str, intents: Intents = Intents.NONE) -> None:
        self.token = token
        self.intents = intents

    @property
    async def _session(self) -> ClientSession:
        if self.__session is None:
            self.__session = ClientSession()
        return self.__session

    async def _request(
        self,
        method: str,
        route: Route,
        *,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        files: dict[str, Any] | None = None
    ) -> Any:
        return await request(
            method,
            route,
            json=json,
            headers={'Authorization': f'Bot {self.token}'} | (headers or {}),
            params=params,
            files=files
        )

    def as_user(self, user_id: int) -> User:
        '''
        Return a user object for the given user ID.

        Intended for sending requests on behalf of a user. e.g. `await app.as_user(123).fetch_member(abc)`

        :param user_id: The user ID to act as.
        :type user_id: `int`
        '''
        return User(user_id=user_id, application=self)

    @overload
    async def fetch_message(
        self,
        message_id: int,
        existence_only: Literal[True],
        max_wait: float = 10.0
    ) -> bool:
        ...

    @overload
    async def fetch_message(
        self,
        message_id: int,
        existence_only: Literal[False],
        max_wait: float = 10.0
    ) -> Message:
        ...

    async def fetch_message(
        self,
        message_id: int,
        existence_only: bool = False,
        max_wait: float = 10.0
    ) -> Message | bool:
        '''
        Fetch a message by either original or proxied ID.

        :param message_id: The original or proxied message ID.
        :type message_id: `int`
        :param only_check_existence: Whether to only check if the message exists. If `True`, the return type will be `bool`.
        :type only_check_existence: `bool`
        :param max_wait: The maximum time to wait for a response. Defaults to 10 seconds.
        :type max_wait: `float`
        :return: `bool` if `only_check_existence` is `True`, otherwise `Message`.
        '''
