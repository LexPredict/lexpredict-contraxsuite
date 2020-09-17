"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

# Standard imports
import importlib
import inspect
import logging
import pydoc
import time
from io import StringIO
from traceback import format_exc

# Third-party imports
from rest_framework.request import Request

# Django imports
from django.conf import settings
from django.http import HttpRequest

# Project imports
from apps.common import redis
from apps.common.models import MethodStats, MethodStatsCollectorPlugin
from apps.common.singleton import Singleton
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_string_db_logger():
    """
    Gets you what you need to log to a string. Returns a pair of StringIO, logger variables.
    >>> output, logger = get_string_db_logger()
    >>> call_stuff_to_debug_with_logger(logger=logger)
    >>> print output.getvalue()
    """
    logger = logging.getLogger('django.db.backends')
    logger.setLevel(logging.DEBUG)
    try:
        fmt = settings.LOGGING['formatters']['verbose']['format']
    except KeyError:
        fmt = "%(levelname)-7s %(asctime)s | %(message)s"
    formatter = logging.Formatter(fmt)
    output = StringIO()
    string_handler = logging.StreamHandler(output)
    string_handler.setFormatter(formatter)
    string_handler.setLevel(logging.DEBUG)
    logger.addHandler(string_handler)

    return output, logger


def collect_stats(name=None, comment=None, log_sql=False, callers_depth=5, batch_size=10, batch_time=60, **kwargs):
    """
    Decorator to collect statistics about function and store in MethodStats object
    Params:
        - name: str - user-defined name of inspecting function
        - comment: str - user-defined comment for a function
        - log_sql: bool - log SQL queries
        - callers_depth: int - how deep introspect to store a caller name, min is 3 for this decorator,
          as the decorator itself adds extra depth
        - batch_size: int - collect data until N items in redis cache, then store in DB
        - batch_time: int - collect data until N seconds in redis cache, then store in DB
        - kwargs: to not raise TypeError let's silently use it fro extra kwargs
    Usage:
    >>> from apps.common.decorators import collect_stats
    >>> @collect_stats(name='My Test for fn', comment='some long comment', log_sql=True)
    >>> def my_method(*args, **kwargs):
    >>>    ....
    This decorator stores timing and SQL into db and a user can easily get all stats
    including some aggregation like
    >>> MethodStats.get(as_dataframe=True, name='My Test for fn')
    """
    def wrapper(func):
        def decorator(*args, **kwargs):
            exception = None
            has_error = False
            error_traceback = None

            if log_sql:
                # setup SQL logger
                output, _ = get_string_db_logger()

            # get timing
            start = time.time()
            try:
                if inspect.ismethod(func):
                    if len(args) <= 1:
                        res = func(**kwargs)
                    else:
                        res = func(args[1:], **kwargs)
                else:
                    res = func(*args, **kwargs)
            except Exception as e:
                res = None
                exception = e
                has_error = True
                error_traceback = format_exc()

            estimate = time.time() - start

            if log_sql:
                # NOTE: in case of querysets - they won't be logged if they are not evaluated yet!
                sql_log = output.getvalue()
            else:
                sql_log = None

            # try to find Request objects and get User
            try:
                user = kwargs['request'].user
            except (KeyError, AttributeError):
                user = None
            if user is None:
                request_objs = [i for i in args if isinstance(i, (HttpRequest, Request))
                                and hasattr(i, 'user') and isinstance(i.user, User)]
                for request_obj in request_objs:
                    if request_obj.user:
                        user = request_obj.user
                        break

            func_name = func.__name__
            fun_args = inspect.signature(func).parameters  # ['self'].__class__.__name__
            if fun_args and 'self' in fun_args:
                func_self = fun_args["self"]
                if func_self:
                    func_name = f'{func_self.__class__.__name__}.{func_name}'

            method_stats = MethodStats(
                user=user,
                time=estimate,
                name=name,
                comment=comment,
                method=func_name,
                path=get_func_path(func, *args, **kwargs),
                description=pydoc.render_doc(func, title='%s', renderer=pydoc.plaintext),
                sql_log=sql_log,
                args=str(args),
                kwargs=str(kwargs),
                # decorator adds extra depth, so set start to 3
                callers=callers(depth=callers_depth, start=3),
                has_error=has_error,
                error_traceback=error_traceback
            )
            cache_key = 'MethodStats_' + name
            cached_res, resume = redis.push_or_pop(cache_key, method_stats, batch_size, batch_time)
            if resume:
                MethodStats.objects.bulk_create(cached_res)

            if exception is not None:
                raise exception

            return res

        decorator._original = func
        return decorator
    return wrapper


def callers(depth=5, start=1):
    return ' >> '.join([caller_name(depth=i) for i in range(depth + 1, start, -1)])


def caller_name(depth=1):
    """Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + depth
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]
    path = get_frame_path(parentframe)

    ## Avoid circular refs and frame leaks
    #  https://docs.python.org/2.7/library/inspect.html#the-interpreter-stack
    del parentframe, stack

    return path


def get_frame_path(frame):
    name = []
    module = inspect.getmodule(frame)
    # `modname` can be None when frame is executed directly in console
    # TODO(techtonik): consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in frame.f_locals:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(frame.f_locals['self'].__class__.__name__)
    codename = frame.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename)   # function or a method

    return ".".join(name)


def get_func_path(func, *args, **kwargs):
    """
    Get function full path including class name:

    :param func:
    :param args:
    :return:
    """
    func_module = inspect.getmodule(func).__name__
    path_parts = [func_module]
    fun_args = inspect.signature(func).parameters
    if 'self' in fun_args:
        # I don't know any way to detect call from the object method
        # XXX: there seems to be no way to detect static method call - it will
        #      be just a function call
        class_name = inspect.signature(func).parameters['self'].__class__.__name__
        path_parts.append(class_name)
    path_parts.append(func.__name__)
    return '.'.join(path_parts)


def get_function_from_str(path):
    module_path = path
    path_parts = path.split('.')
    path_len = len(path_parts)
    try:
        for i in range(1, path_len + 1):
            _module_path = '.'.join(path_parts[:i])
            try:
                importlib.util.find_spec(_module_path)
                module_path = _module_path
            except AttributeError:
                module = importlib.import_module(module_path)
                local_path_chain = path_parts[i - 1:]
                if len(local_path_chain) == 1:
                    method_parent = module
                    method_name = local_path_chain[0]
                else:
                    method_parent = module
                    method_name = local_path_chain[-1]
                    parents_chain = local_path_chain[:-1]
                    for _parent in parents_chain:
                        method_parent = getattr(method_parent, _parent)
                    if type(method_parent) is Singleton:
                        method_parent = method_parent.clz
                method = getattr(method_parent, method_name)
                return method_parent, method, method_name
    except AttributeError:
        pass
    raise RuntimeError('Wrong method path "{}"'.format(path))


def decorate(decorator, path, *args, **kwargs):
    """
    Decorate with collect_stats
    :param decorator: decorator function itself
    :param path: str - absolute import-like-path to a function
        to be decorated like "apps.common.utils.fast_uuid"
    :param args: args passed to a decorator function
    :param kwargs: kwargs passed to a decorator function
    :return: None

    NOTE: it doesn't support nested decorating for now
    """
    method_parent, method, method_name = get_function_from_str(path)

    # NOTE that a decorator should have "_original" attribute to store original method
    original = getattr(method, '_original', None)
    if original is None:
        print('Initiate {} decorator for "{}" method'.format(decorator.__name__, path))
        decorator = decorator(*args, **kwargs)
        setattr(method_parent, method_name, decorator(method))


def undecorate(path):
    """
    Un-decorate with collect_stats
    :param path: str - absolute import-like-path to a function
        to be undecorated like "apps.common.utils.fast_uuid"

    NOTE: it doesn't support nested decorating for now
    """
    method_parent, method, method_name = get_function_from_str(path)
    original = getattr(method, '_original', None)
    if original is not None:
        setattr(method_parent, method_name, original)


def init_decorators():
    """
    Initiate collect_stats decorators on system start
    """
    logging.info('Initiate collect_stats decorators on system start')
    for instance_values in MethodStatsCollectorPlugin.objects.values():
        decorate(collect_stats, **instance_values)
