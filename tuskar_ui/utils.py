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
import re


def de_camel_case(text):
    """Convert CamelCase names to human-readable format."""
    camel_re = re.compile(r'([a-z]|SSL)([A-Z])')
    return camel_re.sub(lambda m: m.group(1) + ' ' + m.group(2), text)
