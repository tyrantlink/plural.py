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
from typing import Self, Annotated

from pydantic import Field, model_validator


from ..types import MissingOr, MissingNoneOr, MISSING, MissingType, PydanticObjectId, Image
from ..errors import Unauthorized, Forbidden, NotFound, BadRequest, MissingIntentError
from .abc import PluralModel, EditableBase
from ..enums import Intents


class ProxyTag(PluralModel):
    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, type(self)) and
            self.prefix == value.prefix and
            self.suffix == value.suffix and
            self.regex == value.regex and
            self.case_sensitive == value.case_sensitive
        )

    prefix: str = Field('', max_length=50)
    '''The prefix of the proxy tag. e.g. {prefix}user{suffix}'''
    suffix: str = Field('', max_length=50)
    '''The suffix of the proxy tag. e.g. {prefix}user{suffix}'''
    regex: bool = False
    '''Whether the prefix and suffix are matched with regex.'''
    case_sensitive: bool = False
    '''Whether the prefix and suffix are case-sensitive.'''

    @model_validator(mode='after')
    def check_prefix_and_suffix(self) -> Self:
        if not self.prefix and not self.suffix:
            raise ValueError(
                'At least one of prefix or suffix must be non-empty')

        return self


class UserProxy(PluralModel):
    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, type(self)) and
            self.user_id == value.user_id and
            self.tag == value.tag
        )

    bot_id: int
    '''The bot ID for the user proxy.'''
    public_key: MissingOr[str] = MISSING
    '''The public key for the user proxy.\n\nRequires the `members.userproxy_tokens.read` intent.'''
    token: MissingNoneOr[str] = MISSING
    '''The token for the user proxy, or `None` if autosync is disabled.\n\nRequires the `members.userproxy_tokens.read` intent.'''
    command: str = 'proxy'  # ! remember to add the regex validation for this
    '''name of the proxy command'''
    include_group_tag: bool = False
    '''Whether to include the group tag in the bot name.'''
    attachment_count: int = Field(1, ge=0, le=10)
    '''The number of attachment options to include in the proxy command.'''
    self_hosted: bool = False
    '''Whether the user proxy is self-hosted.'''
    guilds: set[int] = Field(default_factory=set)
    '''The guild IDs where the user proxy is a member.'''


class Member(PluralModel, EditableBase):
    '''Requires the `members.read` intent.'''
    id: PydanticObjectId
    '''The member ID.'''
    name: str = Field(min_length=1, max_length=80)
    '''The member name. Must be unique within the group and between 1 and 80 characters.'''
    avatar: Image | None = None
    '''The member avatar, if any.'''
    proxy_tags: Annotated[
        list[ProxyTag], Field(max_length=15)
    ] = Field(default_factory=list)
    '''The proxy tags for the member.'''
    userproxy: UserProxy | None = None
    '''The user proxy for the member, if any. Requires the `members.userproxy_tokens.read` intent.'''

    async def edit(
        self,
        name: MissingOr[str] = MISSING,
        avatar: MissingNoneOr[bytes] = MISSING,
        proxy_tags: MissingOr[list[ProxyTag]] = MISSING,
        userproxy: MissingNoneOr[UserProxy] = MISSING
    ) -> None:
        '''
        Edit the member. Requires the `members.write` intent.

        :param name: The member name. Must be unique within the group and between 1 and 80 characters.
        :type name: `str` | `MISSING`
        :param avatar: The member avatar bytes, or `None` to remove the avatar.
        :type avatar: `bytes` | `None` | `MISSING`
        :param proxy_tags: The proxy tags for the member.
        :type proxy_tags: `list[ProxyTag]` | `MISSING`
        :param userproxy: The user proxy for the member, or `None` to remove the user proxy. Requires the `members.userproxy_tokens.write` intent.
        :type userproxy: `UserProxy` | `None` | `MISSING`

        :raises ValueError: A parameter was invalid or Application was not used to create or fetch the member.
        :raises MissingIntentError: The application does not have the required intent.
        :raises Unauthorized: The client is not authorized. Please ensure your token is valid.
        :raises Forbidden: The client is forbidden from accessing the resource. Please ensure the client has the required intents.
        :raises NotFound: The member was not found.
        :raises BadRequest: The request was malformed. Please ensure the request is valid.

        :return: None
        '''

        if not self._app:
            raise ValueError('The member must be created by the application')

        if not self._app.intents & Intents.MEMBERS_WRITE:
            raise MissingIntentError(
                'The application does not have the required intent `members.write`')

        json = {}

        if not isinstance(name, MissingType):
            if not 1 <= len(name) <= 80:
                raise ValueError(
                    'Name must be between 1 and 80 characters')

            json['name'] = name

        if not isinstance(avatar, MissingType):
            #! add image validation
            #! figure out actually uploading images
            ...

        if not isinstance(proxy_tags, MissingType):
            json['proxy_tags'] = proxy_tags

        if not isinstance(userproxy, MissingType):
            if not self._app.intents & Intents.MEMBERS_USERPROXY_TOKEN_WRITE:
                raise MissingIntentError(
                    'The application does not have the required intent `members.userproxy_token.write`')

            json['userproxy'] = userproxy
