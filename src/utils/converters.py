import json
from pprint import pformat

from fastapi.encoders import jsonable_encoder


def to_pretty_json(objects):
    """convert pydantic objects to pretty string in JSON format."""
    return pformat(jsonable_encoder(objects), sort_dicts=False, width=120)


def to_json(objects):
    """
    convert pydantic objects to string in JSON format.
    cf. pydantic_core.to_json returns bytes.
    """
    return json.dumps(jsonable_encoder(objects))
