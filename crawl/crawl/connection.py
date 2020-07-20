import sys
import six
from scrapy.utils.misc import load_object
from . import defaults


# Shortcut maps 'setting name' -> 'parmater name'.
SETTINGS_PARAMS_MAP = {
    'REDIS_URL': 'url',
    'REDIS_HOST': '127.0.0.1',
    'REDIS_PORT': '6379',
    'REDIS_DB': 'db',
    'REDIS_ENCODING': 'encoding',
}

if sys.version_info > (3,):
    SETTINGS_PARAMS_MAP['REDIS_DECODE_RESPONSES'] = 'decode_responses'


def get_redis_instance_from_settings(settings):
    params = defaults.REDIS_PARAMS.copy()
    params.update(settings.getdict('REDIS_PARAMS'))
    for source, dest in SETTINGS_PARAMS_MAP.items():
        val = settings.get(source)
        if val:
            params[dest] = val

    if isinstance(params.get('redis_cls'), six.string_types):
        params['redis_cls'] = load_object(params['redis_cls'])

    return get_redis_instance(**params)

from_settings = get_redis_instance_from_settings

def get_redis_instance(**kwargs):
    redis_cls = kwargs.pop('redis_cls', defaults.REDIS_CLS)
    url = kwargs.pop('url', None)
    if url:
        return redis_cls.from_url(url, **kwargs)
    else:
        return redis_cls(**kwargs)