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
import logging

from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.api import base
from tuskarclient.v1 import client as tuskar_client

from tuskar_ui.api import heat
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa


LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
    return c


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


class OvercloudPlan(base.APIResourceWrapper):
    _attrs = ('id', 'stack_id', 'name', 'description', 'counts', 'attributes')

    def __init__(self, apiresource, request=None):
        super(OvercloudPlan, self).__init__(apiresource)
        self._request = request

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
        return cls.get_the_plan(request)

    # TODO(lsmola) before will will support multiple overclouds, we
    # can work only with overcloud that is named overcloud. Delete
    # this once we have more overclouds. Till then, this is the overcloud
    # that rules them all.
    # This is how API supports it now, so we have to have it this way.
    # Also till Overcloud workflow is done properly, we have to work
    # with situations that overcloud is deleted, but stack is still
    # there. So overcloud will pretend to exist when stack exist.
    @classmethod
    def get_the_plan(cls, request):
        plan_list = cls.list(request)
        for plan in plan_list:
            if plan.name == 'overcloud':
                return plan

    @classmethod
    def delete(cls, request, overcloud_id):
        """Create an Overcloud in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: overcloud id
        :type  overcloud_id: int
        """
        tuskarclient(request).overclouds.delete(overcloud_id)

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

    @cached_property
    def stack(self):
        """Return the Heat Stack associated with this Overcloud

        :return: Heat Stack associated with this Overcloud; or None
                 if no Stack is associated, or no Stack can be
                 found
        :rtype:  heatclient.v1.stacks.Stack or None
        """
        return heat.OvercloudStack.get(self._request, self.stack_id,
                                       plan=self)


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
