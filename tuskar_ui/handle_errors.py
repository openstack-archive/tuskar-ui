# -*- coding: utf8 -*-
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import functools
import inspect

import horizon.exceptions


def handle_errors(error_message, error_default=None):
    """A decorator for adding default error handling to API calls.

    It wraps the original method in a try-except block, with horizon's
    error handling added.

    Note: it should only be used on functions or methods that take
    request as the first (or second after self or cls) argument.

    The decorated method accepts a number of additional parameters:

        :param _error_handle: whether to handle the errors in this call
        :param _error_message: override the error message
        :param _error_default: override the default value returned on error
        :param _error_redirect: specify a redirect url for errors
        :param _error_ignore: ignore known errors
    """
    def decorator(func):
        # XXX This is an ugly hack for finding the 'request' argument.
        for request_pos, name in  enumerate(inspect.getargspec(func).args):
            if name == 'request':
                break
        else:
            raise RuntimeError(
                "The handle_errors decorator requires 'request' as the first "
                "argument of the function or method")
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _error_handle = kwargs.pop('_error_handle', True)
            _error_message = kwargs.pop('_error_message', error_message)
            _error_default = kwargs.pop('_error_default', error_default)
            _error_redirect = kwargs.pop('_error_redirect', None)
            _error_ignore = kwargs.pop('_error_ignore', False)
            if not _error_handle:
                return func(*args, **kwargs)
            try:
                return func(*args, **kwargs)
            except Exception:
                request = args[request_pos]
                horizon.exceptions.handle(request, _error_message,
                                          ignore=_error_ignore,
                                          redirect=_error_redirect)
                return _error_default
        wrapper.wrapped = func
        return wrapper
    return decorator
