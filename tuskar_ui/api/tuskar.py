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

import django.conf
import heatclient
import keystoneclient.exceptions
import logging
import urlparse

from django.utils.translation import ugettext_lazy as _
from horizon.utils import memoized
from openstack_dashboard.api import base
from openstack_dashboard.api import heat
from openstack_dashboard.api import keystone
from tuskarclient.v1 import client as tuskar_client

from tuskar_ui.api import heat as tuskar_heat
from tuskar_ui.api import node
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa

LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


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


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
    return c


def list_to_dict(object_list, key_attribute='id'):
    """Converts an object list to a dict

    :param object_list: list of objects to be put into a dict
    :type  object_list: list

    :param key_attribute: object attribute used as index by dict
    :type  key_attribute: str

    :return: dict containing the objects in the list
    :rtype: dict
    """
    return dict((getattr(o, key_attribute), o) for o in object_list)


def transform_sizing(overcloud_sizing):
    """Transform the sizing to simpler format

    We need this till API will accept the more complex format with flavors,
    then we delete this.

    :param overcloud_sizing: overcloud sizing information with structure
                             {('overcloud_role_id',
                               'flavor_name'): count, ...}
    :type  overcloud_sizing: dict

    :return: list of ('overcloud_role_id', 'num_nodes')
    :rtype:  list
    """
    return [{
        'overcloud_role_id': role,
        'num_nodes': sizing,
    } for (role, flavor), sizing in overcloud_sizing.items()]


class Overcloud(base.APIResourceWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description', 'counts', 'attributes')

    def __init__(self, apiresource, request=None):
        super(Overcloud, self).__init__(apiresource)
        self._request = request

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
                self.attributes.get('AdminPassword', None))
        except keystoneclient.exceptions.Unauthorized:
            LOG.debug('Unable to connect overcloud keystone.')
            return None

    @classmethod
    def create(cls, request, overcloud_sizing, overcloud_configuration):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_sizing: overcloud sizing information with structure
                                 {('overcloud_role_id',
                                   'flavor_name'): count, ...}
        :type  overcloud_sizing: dict

        :param overcloud_configuration: overcloud configuration with structure
                                        {'key': 'value', ...}
        :type  overcloud_configuration: dict

        :return: the created Overcloud object
        :rtype:  tuskar_ui.api.Overcloud
        """
        # TODO(lsmola) for now we have to transform the sizing to simpler
        # format, till API will accept the more complex with flavors,
        # then we delete this
        transformed_sizing = transform_sizing(overcloud_sizing)

        overcloud = tuskarclient(request).overclouds.create(
            name='overcloud', description="Openstack cloud providing VMs",
            counts=transformed_sizing, attributes=overcloud_configuration)

        return cls(overcloud, request=request)

    @classmethod
    def update(cls, request, overcloud_id, overcloud_sizing,
               overcloud_configuration):
        """Update an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: id of the overcloud we want to update
        :type  overcloud_id: string

        :param overcloud_sizing: overcloud sizing information with structure
                                 {('overcloud_role_id',
                                   'flavor_name'): count, ...}
        :type  overcloud_sizing: dict

        :param overcloud_configuration: overcloud configuration with structure
                                        {'key': 'value', ...}
        :type  overcloud_configuration: dict

        :return: the updated Overcloud object
        :rtype:  tuskar_ui.api.Overcloud
        """
        # TODO(lsmola) for now we have to transform the sizing to simpler
        # format, till API will accept the more complex with flavors,
        # then we delete this
        transformed_sizing = transform_sizing(overcloud_sizing)

        overcloud = tuskarclient(request).overclouds.update(
            overcloud_id, counts=transformed_sizing,
            attributes=overcloud_configuration)

        return cls(overcloud, request=request)

    @classmethod
    def list(cls, request):
        """Return a list of Overclouds in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overclouds, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Overcloud
        """
        ocs = tuskarclient(request).overclouds.list()

        return [cls(oc, request=request) for oc in ocs]

    @classmethod
    def template_parameters(cls, request):
        """Return a list of needed template parameters

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: dict with key/value parameters
        :rtype:  dict
        """
        parameters = tuskarclient(request).overclouds.template_parameters()
        # FIXME(lsmola) python client is converting the result to
        # object, we have to return it better from client or API
        return parameters._info

    @classmethod
    @handle_errors(_("Unable to retrieve deployment"))
    def get(cls, request, overcloud_id):
        """Return the Tuskar Overcloud that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: ID of Overcloud to be retrieved
        :type  overcloud_id: int

        :return: matching Overcloud, or None if no Overcloud matches
                 the ID
        :rtype:  tuskar_ui.api.Overcloud
        """
        # FIXME(lsmola) hack for Icehouse, only one Overcloud is allowed
        # TODO(lsmola) uncomment when possible
        # overcloud = tuskarclient(request).overclouds.get(overcloud_id)
        # return cls(overcloud, request=request)
        return cls.get_the_overcloud(request)

    # TODO(lsmola) before will will support multiple overclouds, we
    # can work only with overcloud that is named overcloud. Delete
    # this once we have more overclouds. Till then, this is the overcloud
    # that rules them all.
    # This is how API supports it now, so we have to have it this way.
    # Also till Overcloud workflow is done properly, we have to work
    # with situations that overcloud is deleted, but stack is still
    # there. So overcloud will pretend to exist when stack exist.
    @classmethod
    def get_the_overcloud(cls, request):
        overcloud_list = cls.list(request)
        for overcloud in overcloud_list:
            if overcloud.name == 'overcloud':
                return overcloud

        the_overcloud = cls(object(), request=request)
        # I need to mock attributes of overcloud that is being deleted.
        the_overcloud.id = "overcloud"

        if the_overcloud.stack and the_overcloud.is_deleting:
            return the_overcloud
        else:
            raise heatclient.exc.HTTPNotFound()

    @classmethod
    def delete(cls, request, overcloud_id):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: overcloud id
        :type  overcloud_id: int
        """
        tuskarclient(request).overclouds.delete(overcloud_id)

    @cached_property
    def stack(self):
        """Return the Heat Stack associated with this Overcloud

        :return: Heat Stack associated with this Overcloud; or None
                 if no Stack is associated, or no Stack can be
                 found
        :rtype:  heatclient.v1.stacks.Stack or None
        """
        return heat.stack_get(self._request, 'overcloud')

    @cached_property
    def stack_events(self):
        """Return the Heat Events associated with this Overcloud

        :return: list of Heat Events associated with this Overcloud;
                 or an empty list if there is no Stack associated with
                 this Overcloud, or there are no Events
        :rtype:  list of heatclient.v1.events.Event
        """
        if self.stack:
            return heat.events_list(self._request,
                                    self.stack.stack_name)
        return []

    @cached_property
    def is_deployed(self):
        """Check if this Overcloud is successfully deployed.

        :return: True if this Overcloud is successfully deployed;
                 False otherwise
        :rtype:  bool
        """
        return self.stack.stack_status in ('CREATE_COMPLETE',
                                           'UPDATE_COMPLETE')

    @cached_property
    def is_deploying(self):
        """Check if this Overcloud is currently deploying or updating.

        :return: True if deployment is in progress, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('CREATE_IN_PROGRESS',
                                           'UPDATE_IN_PROGRESS')

    @cached_property
    def is_failed(self):
        """Check if this Overcloud failed to update or deploy.

        :return: True if deployment there was an error, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('CREATE_FAILED',
                                           'UPDATE_FAILED',)

    @cached_property
    def is_deleting(self):
        """Check if this Overcloud is deleting.

        :return: True if Overcloud is deleting, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('DELETE_IN_PROGRESS', )

    @cached_property
    def is_delete_failed(self):
        """Check if this Overcloud deleting has failed.

        :return: True if Overcloud deleting has failed, False otherwise.
        :rtype: bool
        """
        return self.stack.stack_status in ('DELETE_FAILED', )

    @memoized.memoized
    def all_resources(self, with_joins=True):
        """Return a list of all Overcloud Resources

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of all Overcloud Resources or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.Resource
        """
        try:
            resources = [r for r in heat.resources_list(self._request,
                                                        self.stack.stack_name)]
        except heatclient.exc.HTTPInternalServerError:
            # TODO(lsmola) There is a weird bug in heat, that after
            # stack-create it returns 500 for a little while. This can be
            # removed once the bug is fixed.
            resources = []

        if not with_joins:
            return [tuskar_heat.Resource(r, request=self._request)
                    for r in resources]

        nodes_dict = list_to_dict(node.Node.list(self._request,
                                                 associated=True),
                                  key_attribute='instance_uuid')
        joined_resources = []
        for r in resources:
            joined_resources.append(
                tuskar_heat.Resource(r,
                                     node=nodes_dict.get(
                                         r.physical_resource_id, None),
                                     request=self._request))
        # TODO(lsmola) I want just resources with nova instance
        # this could be probably filtered a better way, investigate
        return [r for r in joined_resources if r.node is not None]

    @memoized.memoized
    def resources(self, overcloud_role, with_joins=True):
        """Return a list of Overcloud Resources that match an Overcloud Role

        :param overcloud_role: role of resources to be returned
        :type  overcloud_role: tuskar_ui.api.OvercloudRole

        :param with_joins: should we also retrieve objects associated with each
                           retrieved Resource?
        :type  with_joins: bool

        :return: list of Overcloud Resources that match the Overcloud Role,
                 or an empty list if there are none
        :rtype:  list of tuskar_ui.api.Resource
        """
        # FIXME(lsmola) with_joins is not necessary here, I need at least
        # nova instance
        all_resources = self.all_resources(with_joins)
        filtered_resources = [resource for resource in all_resources if
                              (overcloud_role.is_deployed_on_node(
                                  resource.node))]

        return filtered_resources

    @memoized.memoized
    def resources_count(self, overcloud_role=None):
        """Return count of Overcloud Resources

        :param overcloud_role: role of resources to be counted, None means all
        :type  overcloud_role: tuskar_ui.api.OvercloudRole

        :return: Number of matches resources
        :rtype:  int
        """
        # TODO(dtantsur): there should be better way to do it, rather than
        # fetching and calling len()
        # FIXME(dtantsur): should also be able to use with_joins=False
        # but unable due to bug #1289505
        if overcloud_role is None:
            resources = self.all_resources()
        else:
            resources = self.resources(overcloud_role)
        return len(resources)

    @cached_property
    def stack_outputs(self):
        return getattr(self.stack, 'outputs', [])

    @cached_property
    def keystone_ip(self):
        for output in self.stack_outputs:
            if output['output_key'] == 'KeystoneURL':
                return urlparse.urlparse(output['output_value']).hostname

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


class OvercloudRole(base.APIResourceWrapper):
    _attrs = ('id', 'name', 'description', 'image_name', 'flavor_id')

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud roles"), [])
    def list(cls, request):
        """Return a list of Overcloud Roles in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overcloud Roles, or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.OvercloudRole
        """
        roles = tuskarclient(request).overcloud_roles.list()
        return [cls(role) for role in roles]

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get(cls, request, role_id):
        """Return the Tuskar OvercloudRole that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param role_id: ID of OvercloudRole to be retrieved
        :type  role_id: int

        :return: matching OvercloudRole, or None if no matching
                 OvercloudRole can be found
        :rtype:  tuskar_ui.api.OvercloudRole
        """
        role = tuskarclient(request).overcloud_roles.get(role_id)
        return cls(role)

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get_by_node(cls, request, node):
        """Return the Tuskar OvercloudRole that is deployed on the node

        :param request: request object
        :type  request: django.http.HttpRequest

        :param node: node to check against
        :type  node: tuskar_ui.api.node.Node

        :return: matching OvercloudRole, or None if no matching
                 OvercloudRole can be found
        :rtype:  tuskar_ui.api.OvercloudRole
        """
        roles = cls.list(request)
        for role in roles:
            if role.is_deployed_on_node(node):
                return role

    def update(self, request, **kwargs):
        """Update the selected attributes of Tuskar OvercloudRole.

        :param request: request object
        :type  request: django.http.HttpRequest
        """
        for attr in kwargs:
            if attr not in self._attrs:
                raise TypeError('Invalid parameter %r' % attr)
        tuskarclient(request).overcloud_roles.update(self.id, **kwargs)

    def is_deployed_on_node(self, node):
        """Determine whether a node matches an overcloud role

        :param node: node to check against
        :type  node: tuskar_ui.api.node.Node

        :return: does this node match the overcloud_role?
        :rtype:  bool
        """
        return self.image_name == node.image_name
