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

import django.forms
import django.template


register = django.template.Library()


@register.filter
def add_bootstrap_class(field):
    """
    Add a "form-control" CSS class to the field's widget.

    This is so that Bootstrap styles it properly.
    """
    if not isinstance(field, (
        django.forms.CheckboxInput,
        django.forms.CheckboxSelectMultiple,
        django.forms.RadioSelect,
        django.forms.FileInput,
        str,
    )):
        field_classes = set(field.field.widget.attrs.get('class', '').split())
        field_classes.add('form-control')
        field.field.widget.attrs['class'] = ' '.join(field_classes)
    return field
