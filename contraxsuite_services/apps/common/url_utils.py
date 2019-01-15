from typing import List, Dict, Any, Optional


class URLParamFormatException(Exception):
    pass


def as_bool(url_params: Dict[str, Any], name: str, default_value: Optional[bool] = None) -> Optional[bool]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    url_param = url_param.strip().lower()
    if 'true' == url_param:
        return True
    elif 'false' == url_param:
        return False
    else:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: true or false'
                                      '\nGot: {1}'.format(name, url_param))


def as_int(url_params: Dict[str, Any], name: str, default_value: Optional[int] = None) -> Optional[int]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value

    try:
        return int(url_param)
    except ValueError:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: integer number (e.g.: 42)'
                                      '\nGot: {1}'.format(name, url_param))


def as_int_list(url_params: Dict[str, Any], name: str, default_value: Optional[List[int]] = None) \
        -> Optional[List[int]]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    try:
        return [int(s.strip()) for s in url_param.split(',')]
    except:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: comma-separated list of integer numbers (e.g.: 1,2,3)'
                                      '\nGot: {1}'.format(name, url_param))


def as_str_list(url_params: Dict[str, Any], name: str, default_value: Optional[List[str]] = None) \
        -> Optional[List[str]]:
    url_param = url_params.get(name)
    if url_param is None:
        return default_value
    try:
        return [str(s.strip()) for s in url_param.split(',')]
    except:
        raise URLParamFormatException('Unable to parse URL parameter {0}'
                                      '\nExpected: comma-separated list of strings (e.g.: aaa,bbb,ccc)'
                                      '\nGot: {1}'.format(name, url_param))
