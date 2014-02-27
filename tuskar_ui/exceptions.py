# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

from openstack_dashboard import exceptions
from tuskarclient.openstack.common.apiclient import exceptions as tuskarclient

NOT_FOUND = exceptions.NOT_FOUND
RECOVERABLE = exceptions.RECOVERABLE + (tuskarclient.ClientException,)
UNAUTHORIZED = exceptions.UNAUTHORIZED


def handle_errors(error_message, error_default=None):
    """A decorator for adding default error handling to API calls.

    It wraps the original method in a try-except block, with horizon's
    error handling added.

    Note: it should only be used on methods that take request as the first
    (second after self or cls) argument.

    The decorated metod accepts a number of additional parameters:

        :param _error_handle: whether to handle the errors in this call
        :param _error_message: override the error message
        :param _error_default: override the default value returned on error
        :param _error_redirect: specify a redirect url for errors
        :param _error_ignore: ignore known errors
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            _error_handle = kwargs.pop('_error_handle', True)
            _error_message = kwargs.pop('_error_message', error_message)
            _error_default = kwargs.pop('_error_default', error_default)
            _error_redirect = kwargs.pop('_error_redirect', None)
            _error_ignore = kwargs.pop('_error_ignore', False)
            if not _error_handle:
                return func(self, request, *args, **kwargs)
            try:
                return func(self, request, *args, **kwargs)
            except Exception:
                exceptions.handle(request, _error_message,
                                  ignore=_error_ignore,
                                  redirect=_error_redirect)
                return _error_default
        wrapper.wrapped = func
        return wrapper
    return decorator
