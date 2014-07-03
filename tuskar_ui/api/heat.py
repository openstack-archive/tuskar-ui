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

import heatclient
import keystoneclient.exceptions
import logging
import urlparse

from horizon.utils import memoized

from openstack_dashboard.api import base
from openstack_dashboard.api import heat
from openstack_dashboard.api import keystone

from tuskar_ui.api import node
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui import utils


LOG = logging.getLogger(__name__)


def overcloud_keystoneclient(request, endpoint, password):
    """Returns a client connected to the Keystone backend.

    Several forms of authentication are supported:

        * Username + password -> Unscoped authentication
        * Username + password + tenant id -> Scoped authentication
        * Unscoped token -> Unscoped authentication
        * Unscoped token + tenant id -> Scoped authentication
        * Scoped token -> Scoped authentication

    Available services and data from the backend will vary depending on
    whether the authentication was scoped or unscoped.

    Lazy authentication if an ``endpoint`` parameter is provided.

    Calls requiring the admin endpoint should have ``admin=True`` passed in
    as a keyword argument.

    The client is cached so that subsequent API calls during the same
    request/response cycle don't have to be re-authenticated.
    """
    api_version = keystone.VERSIONS.get_active_version()

    # TODO(lsmola) add support of certificates and secured http and rest of
    # parameters according to horizon and add configuration to local settings
    # (somehow plugin based, we should not maintain a copy of settings)
    LOG.debug("Creating a new keystoneclient connection to %s." % endpoint)

    # TODO(lsmola) we should create tripleo-admin user for this purpose
    # this needs to be done first on tripleo side
    conn = api_version['client'].Client(username="admin",
                                        password=password,
                                        tenant_name="admin",
                                        auth_url=endpoint)

    return conn


class OvercloudStack(base.APIResourceWrapper):
    _attrs = ('id', 'stack_name', 'outputs', 'stack_status', 'parameters')

    def __init__(self, apiresource, request=None, plan=None):
        super(OvercloudStack, self).__init__(apiresource)
        self._request = request
        self._plan = plan

    @classmethod
    def get(cls, request, stack_id, plan=None):
        """Return the Heat Stack associated with the stack_id

        :return: Heat Stack associated with the stack_id; or None
                 if no Stack is associated, or no Stack can be
                 found
        :rtype:  heatclient.v1.stacks.Stack or None
        """
        stack = heat.stack_get(request, stack_id)
        return cls(stack, request=request, plan=plan)

    @memoized.memoized
    def resources(self, with_joins=True):
        """Return a list of all Resources associated with the Stack

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of all Resources or an empty list if there are none
        :rtype:  list of tuskar_ui.api.heat.Resource
        """
        try:
            resources = [r for r in heat.resources_list(self._request,
                                                        self.stack_name)]
        except heatclient.exc.HTTPInternalServerError:
            # TODO(lsmola) There is a weird bug in heat, that after
            # stack-create it returns 500 for a little while. This can be
            # removed once the bug is fixed.
            resources = []

        if not with_joins:
            return [Resource(r, request=self._request)
                    for r in resources]

        nodes_dict = utils.list_to_dict(node.Node.list(self._request,
                                                       associated=True),
                                        key_attribute='instance_uuid')
        joined_resources = []
        for r in resources:
            joined_resources.append(
                Resource(r, node=nodes_dict.get(r.physical_resource_id, None),
                         request=self._request))
        # TODO(lsmola) I want just resources with nova instance
        # this could be probably filtered a better way, investigate
        return [r for r in joined_resources if r.node is not None]

    @memoized.memoized
    def resources_by_role(self, overcloud_role, with_joins=True):
        """Return a list of Resources that match an OvercloudRole

        :param overcloud_role: role of resources to be returned
        :type  overcloud_role: tuskar_ui.api.tuskar.OvercloudRole

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of Resources that match the OvercloudRole, or an empty
                 list if there are none
        :rtype:  list of tuskar_ui.api.heat.Resource
        """
        # FIXME(lsmola) with_joins is not necessary here, I need at least
        # nova instance
        resources = self.resources(with_joins)
        filtered_resources = [resource for resource in resources if
                              (overcloud_role.is_deployed_on_node(
                                  resource.node))]

        return filtered_resources

    @memoized.memoized
    def resources_count(self, overcloud_role=None):
        """Return count of associated Resources

        :param overcloud_role: role of resources to be counted; None means all
        :type  overcloud_role: tuskar_ui.api.tuskar.OvercloudRole

        :return: Number of matching resources
        :rtype:  int
        """
        # TODO(dtantsur): there should be better way to do it, rather than
        # fetching and calling len()
        # FIXME(dtantsur): should also be able to use with_joins=False
        # but unable due to bug #1289505
        if overcloud_role is None:
            resources = self.resources()
        else:
            resources = self.resources_by_role(overcloud_role)
        return len(resources)

    @cached_property
    def is_deployed(self):
        """Check if this Stack is successfully deployed.

        :return: True if this Stack is successfully deployed, False otherwise
        :rtype:  bool
        """
        return self.stack_status in ('CREATE_COMPLETE',
                                     'UPDATE_COMPLETE')

    @cached_property
    def is_deploying(self):
        """Check if this Stack is currently deploying or updating.

        :return: True if deployment is in progress, False otherwise.
        :rtype: bool
        """
        return self.stack_status in ('CREATE_IN_PROGRESS',
                                     'UPDATE_IN_PROGRESS')

    @cached_property
    def is_failed(self):
        """Check if this Stack failed to update or deploy.

        :return: True if deployment there was an error, False otherwise.
        :rtype: bool
        """
        return self.stack_status in ('CREATE_FAILED',
                                     'UPDATE_FAILED',)

    @cached_property
    def is_deleting(self):
        """Check if this Stack is deleting.

        :return: True if Stack is deleting, False otherwise.
        :rtype: bool
        """
        return self.stack_status in ('DELETE_IN_PROGRESS', )

    @cached_property
    def is_delete_failed(self):
        """Check if Stack deleting has failed.

        :return: True if Stack deleting has failed, False otherwise.
        :rtype: bool
        """
        return self.stack_status in ('DELETE_FAILED', )

    @cached_property
    def events(self):
        """Return the Heat Events associated with this Stack

        :return: list of Heat Events associated with this Stack;
                 or an empty list if there is no Stack associated with
                 this Stack, or there are no Events
        :rtype:  list of heatclient.v1.events.Event
        """
        return heat.events_list(self._request,
                                self.stack_name)
        return []

    @property
    def stack_outputs(self):
        return getattr(self, 'outputs', [])

    @cached_property
    def keystone_ip(self):
        for output in self.stack_outputs:
            if output['output_key'] == 'KeystoneURL':
                return urlparse.urlparse(output['output_value']).hostname

    @cached_property
    def overcloud_keystone(self):
        for output in self.stack_outputs:
            if output['output_key'] == 'KeystoneURL':
                break
        else:
            return None
        try:
            return overcloud_keystoneclient(
                self._request,
                output['output_value'],
                self._plan.attributes.get('AdminPassword', None))
        except keystoneclient.exceptions.Unauthorized:
            LOG.debug('Unable to connect overcloud keystone.')
            return None

    @cached_property
    def dashboard_urls(self):
        client = self.overcloud_keystone
        if not client:
            return []

        services = client.services.list()

        for service in services:
            if service.name == 'horizon':
                break
        else:
            return []

        admin_urls = [endpoint.adminurl for endpoint
                      in client.endpoints.list()
                      if endpoint.service_id == service.id]

        return admin_urls


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
        :type  node: tuskar_ui.api.node.Node

        :return: Resource object
        :rtype:  Resource
        """
        super(Resource, self).__init__(apiresource)
        self._request = request
        if 'node' in kwargs:
            self._node = kwargs['node']

    @classmethod
    def get(cls, request, stack, resource_name):
        """Return the specified Heat Resource within a Stack

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud: the Stack from which to retrieve the resource
        :type  overcloud: tuskar_ui.api.heat.OvercloudStack

        :param resource_name: name of the Resource to retrieve
        :type  resource_name: str

        :return: matching Resource, or None if no Resource in the Stack
                 matches the resource name
        :rtype:  tuskar_ui.api.heat.Resource
        """
        resource = heat.resource_get(stack.id,
                                     resource_name)
        return cls(resource, request=request)

    @cached_property
    def node(self):
        """Return the Ironic Node associated with this Resource

        :return: Ironic Node associated with this Resource, or None if no
                 Node is associated
        :rtype:  tuskar_ui.api.node.Node

        :raises: ironicclient.exc.HTTPNotFound if there is no Node with the
                 matching instance UUID
        """
        if hasattr(self, '_node'):
            return self._node
        if self.physical_resource_id:
            return node.Node.get_by_instance_uuid(self._request,
                                                  self.physical_resource_id)
        return None
