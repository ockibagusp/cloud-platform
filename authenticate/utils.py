from calendar import timegm
from datetime import datetime
from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(node):
    payload = {
        'id': node.id,
        'label': node.label,
        'subsperday': node.subsperday,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }

    # Include original issued at time for a brand new token,
    # to allow token refresh
    if api_settings.JWT_ALLOW_REFRESH:
        payload['orig_iat'] = timegm(
            datetime.utcnow().utctimetuple()
        )

    if api_settings.JWT_AUDIENCE is not None:
        payload['aud'] = api_settings.JWT_AUDIENCE

    if api_settings.JWT_ISSUER is not None:
        payload['iss'] = api_settings.JWT_ISSUER

    return payload


def jwt_get_label_from_payload_handler(payload):
    """
    Override this function if label is formatted differently in payload
    """
    return payload.get('label')
