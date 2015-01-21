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
    return {'items': [role.to_dict() for role in roles]}
