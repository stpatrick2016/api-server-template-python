import datetime

from flask.json import JSONEncoder
from pydantic import typing


class CustomJsonEncoder(JSONEncoder):
    def default(self, obj: typing.Any) -> typing.Any:
        try:
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        return JSONEncoder.default(self, obj)
