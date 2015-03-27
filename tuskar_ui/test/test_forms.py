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


from django.utils.translation import ugettext_lazy as _

from tuskar_ui import forms
from tuskar_ui.test import helpers as test


class MultiMACFieldTests(test.TestCase):
    def test_empty(self):
        field = forms.MultiMACField(required=False)
        cleaned = field.clean("")
        self.assertEqual(cleaned, "")

    def test_required(self):
        field = forms.MultiMACField(required=True)
        with self.assertRaises(forms.forms.ValidationError) as raised:
            field.clean("")
        self.assertEqual(unicode(raised.exception.messages[0]),
                         unicode(_('This field is required.')))

    def test_malformed(self):
        field = forms.MultiMACField(required=True)
        with self.assertRaises(forms.forms.ValidationError) as raised:
            field.clean("de.ad:be.ef:ca.fe")
        self.assertEqual(
            unicode(raised.exception.messages[0]),
            unicode(_(u"'de.ad:be.ef:ca.fe' is not a valid MAC address.")),
        )

    def test_single(self):
        field = forms.MultiMACField(required=False)
        cleaned = field.clean("de:AD:be:ef:Ca:FE")
        self.assertEqual(cleaned, "DE:AD:BE:EF:CA:FE")

    def test_multiple(self):
        field = forms.MultiMACField(required=False)
        cleaned = field.clean(
            "de:AD:be:ef:Ca:FC, de:AD:be:ef:Ca:FD de:AD:be:ef:Ca:FE\n"
            "de:AD:be:ef:Ca:FF",
        )
        self.assertEqual(
            cleaned,
            "DE:AD:BE:EF:CA:FC DE:AD:BE:EF:CA:FD DE:AD:BE:EF:CA:FE "
            "DE:AD:BE:EF:CA:FF",
        )

    def test_duplicated(self):
        field = forms.MultiMACField(required=False)
        with self.assertRaises(forms.forms.ValidationError) as raised:
                field.clean("DE:AD:BE:EF:CA:FC DE:AD:BE:EF:CA:FC")

        self.assertEqual(
            unicode(raised.exception.messages[0]),
            unicode(_("Duplicated MAC addresses.")),
        )
