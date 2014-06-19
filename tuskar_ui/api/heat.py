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

import logging

from openstack_dashboard.api import base
from openstack_dashboard.api import heat

from tuskar_ui.api import node
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa

LOG = logging.getLogger(__name__)


class Resource(base.APIResourceWrapper):
    _attrs = ('resource_name', 'resource_type', 'resource_status',
              'physical_resource_id')

    def __init__(self, apiresource, request=None, **kwargs):
        """Initialize a resource

        :param apiresource: apiresource we want to wrap
        :type  apiresource: heatclient.v1.resources.Resource

        :param request: request
        :type  request: django.core.handlers.wsgi.WSGIRequest

        :param node: node relation we want to cache
        :type  node: tuskar_ui.api.Node

        :return: Resource object
        :rtype:  Resource
        """
        super(Resource, self).__init__(apiresource)
        self._request = request
        if 'node' in kwargs:
            self._node = kwargs['node']

    @classmethod
    def get(cls, request, overcloud, resource_name):
        """Return the specified Heat Resource within an Overcloud

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud: the Overcloud from which to retrieve the resource
        :type  overcloud: tuskar_ui.api.Overcloud

        :param resource_name: name of the Resource to retrieve
        :type  resource_name: str

        :return: matching Resource, or None if no Resource in the Overcloud
                 stack matches the resource name
        :rtype:  tuskar_ui.api.Resource
        """
        resource = heat.resource_get(overcloud.stack.id,
                                     resource_name)
        return cls(resource, request=request)

    @cached_property
    def node(self):
        """Return the Ironic Node associated with this Resource

        :return: Ironic Node associated with this Resource, or None if no
                 Node is associated
        :rtype:  tuskar_ui.api.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with the
                 matching instance UUID
        """
        if hasattr(self, '_node'):
            return self._node
        if self.physical_resource_id:
            return node.Node.get_by_instance_uuid(self._request,
                                                  self.physical_resource_id)
        return None
