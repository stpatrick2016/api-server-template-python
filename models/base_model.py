from __future__ import annotations

import datetime
import json
import typing
from uuid import uuid4

from pydantic import BaseModel, Field


class ApiBaseModel(BaseModel):
    """
    Base class for all models
    """

    def serialize(self) -> typing.MutableMapping:
        """
        Serializes object to dictionary
        """
        return self.dict(by_alias=True)

    def to_json(self) -> str:
        """
        Serializes object into JSON string
        """
        return (
            json.dumps(
                self.serialize(),
                ensure_ascii=False,
                default=ApiBaseModel._json_serializer,
            )
            .encode("utf-8")
            .decode()
        )

    @staticmethod
    def _json_serializer(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        raise TypeError(f"Type {type(obj)} is not serializable")

    @classmethod
    def deserialize(cls, data: typing.MutableMapping):
        """
        Deserializes dictionary to object instance
        :param data: Dictionary to deserialize from
        :return: Fully populated object with data from dictionary
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> ApiBaseModel:
        """
        Deserializes JSON string to object
        :param json_str: JSON formatted string
        """
        return cls.deserialize(json.loads(json_str))


class ApiBaseModelWithId(ApiBaseModel):
    """
    Base class for models that have unique ID
    """

    id: str = Field(default_factory=lambda: uuid4().hex)
