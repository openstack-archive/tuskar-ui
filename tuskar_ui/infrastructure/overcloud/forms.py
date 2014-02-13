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

from django.utils.translation import ugettext_lazy as _  # noqa

from horizon import exceptions
from horizon import forms
from horizon import messages

from tuskar_ui import api


class UndeployOvercloud(forms.SelfHandlingForm):
    def handle(self, request, data):
        try:
            api.Overcloud.delete(request, self.initial['overcloud_id'])
        except Exception:
            exceptions.handle(request, _("Unable to undeploy overcloud."))
            return False
        else:
            msg = _('Undeployment in progress.')
            messages.success(request, msg)
            return True
