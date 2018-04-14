from bson import ObjectId
from bson.errors import InvalidId
import re


def is_objectid_valid(oid):
    try:
        ObjectId(oid)
        return True
    except (InvalidId, TypeError):
        return False


def is_url_regex_match(regex, url_path):
    if re.match(regex, url_path):
        return True
    return False
