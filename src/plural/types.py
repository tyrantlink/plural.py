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
from typing import Literal, Any, TypeVar, Self

from pydantic_core.core_schema import ValidationInfo, str_schema
from pydantic import GetJsonSchemaHandler, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue
from pydantic.validators import plain_validator
from bson.objectid import ObjectId, InvalidId

from .enums import ImageExtension


__all__ = (
    'PydanticObjectId',
    'MISSING',
    'MissingType',
    'Image',
    'MissingOr',
    'MissingNoneOr',
)


class MissingType:
    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "MISSING"

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(
        self,
        _: Any  # noqa: ANN401
    ) -> Self:
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # noqa: ANN401
        _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.none_schema(),
            python_schema=core_schema.is_instance_schema(cls),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: CoreSchema,
        _handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "null"}


class PydanticObjectId(ObjectId):
    """
    Object Id field. Compatible with Pydantic.
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _: ValidationInfo):
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        try:
            return PydanticObjectId(v)
        except (InvalidId, TypeError):
            raise ValueError("Id must be of type PydanticObjectId")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:  # type: ignore
        return core_schema.json_or_python_schema(
            python_schema=plain_validator(cls.validate),
            json_schema=str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance), when_used="json"
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,  # type: ignore
    ) -> JsonSchemaValue:
        json_schema = handler(schema)
        json_schema.update(
            type="string",
            example="5eb7cf5a86d9755df3a6c593",
        )
        return json_schema


MISSING = MissingType()

T = TypeVar('T')
MissingOr = T | MissingType
MissingNoneOr = T | None | MissingType


class Image:
    def __init__(self, image_data: bytes, parent_id: PydanticObjectId) -> None:
        self.extension = ImageExtension(image_data[0])
        self.hash = image_data[1:].hex()
        self._parent_id = parent_id

    def __bytes__(self) -> bytes:
        return self.extension.value.to_bytes() + bytes.fromhex(self.hash)

    def __str__(self) -> str:
        return bytes(self).hex()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self)) and
            self.extension == other.extension and
            self.hash == other.hash
        )

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # noqa: ANN401
        _handler: GetJsonSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.bytes_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.bytes_schema(),
                core_schema.no_info_plain_validator_function(cls.validate)
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
                when_used='json'
            )
        )

    @property
    def url(self) -> str:
        """The CDN URL of the avatar."""
        #! figure out how to make this with a modifiable base_url
        return f'https://cdn.plural.gg/images/{self._parent_id}/{self.hash}.{self.extension.name.lower()}'

    @property
    def ext(self) -> str:
        """The string file extension of the image. e.g. 'png'"""
        return self.extension.name.lower()
