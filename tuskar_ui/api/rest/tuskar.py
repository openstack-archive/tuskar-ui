# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API over the tuskar service.
"""

from django.views import generic

from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils

from tuskar_ui import api


@urls.register
class Roles(generic.View):
  """API for Tuskar Roles.
  """
  url_regex = r'tuskar/roles/$'

  @rest_utils.ajax()
  def get(self, request):
    """Get list of Roles.
    """
    roles = api.tuskar.Role.list(request)
    plan = api.tuskar.Plan.get_the_plan(request)

    roles_data = []

    for role in roles:
        data = role.to_dict()

        role_flavor = role.flavor(plan)
        if role_flavor:
            data['flavor'] = role_flavor.name
        else:
            data['flavor'] = _('Unknown')

        try:
            role_image = role.image(plan)
        except glance_exc.HTTPNotFound:
            # Glance returns a 404 if the image doesn't exist
            role_image = None
        if role_image:
            data['image'] = role_image.name
        else:
            data['image'] = _('Unknown')

        roles_data.append(data)

    return {'items': roles_data}
