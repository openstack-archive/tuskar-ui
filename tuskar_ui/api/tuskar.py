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
from openstack_dashboard.test.test_data import utils
from tuskarclient.v1 import client as tuskar_client

from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa
from tuskar_ui.test.test_data import tuskar_data


TEST_DATA = utils.TestDataContainer()
tuskar_data.data(TEST_DATA)

LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.Client(TUSKAR_ENDPOINT_URL)
    return c


class OvercloudPlan(base.APIDictWrapper):
    _attrs = ('id', 'name', 'description', 'created_at', 'modified_at',
              'roles', 'parameters')

    def __init__(self, apiresource, request=None):
        super(OvercloudPlan, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, name, description):
        """Create an OvercloudPlan in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param name: plan name
        :type  name: string

        :param description: plan description
        :type  description: string

        :return: the created OvercloudPlan object
        :rtype:  tuskar_ui.api.tuskar.OvercloudPlan
        """

        return cls(TEST_DATA.tuskarclient_plans.first(),
                   request=request)

    @classmethod
    def update(cls, request, overcloud_id, name, description):
        """Update an OvercloudPlan in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param overcloud_id: id of the overcloud we want to update
        :type  overcloud_id: string

        :param name: plan name
        :type  name: string

        :param description: plan description
        :type  description: string

        :return: the updated OvercloudPlan object
        :rtype:  tuskar_ui.api.tuskar.OvercloudPlan
        """
        return cls(TEST_DATA.tuskarclient_plans.first(),
                   request=request)

    @classmethod
    def list(cls, request):
        """Return a list of OvercloudPlans in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of OvercloudPlans, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.tuskar.OvercloudPlan
        """
        plans = TEST_DATA.tuskarclient_plans.list()

        return [cls(plan, request=request) for plan in plans]

    @classmethod
    @handle_errors(_("Unable to retrieve plan"))
    def get(cls, request, plan_id):
        """Return the OvercloudPlan that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: id of OvercloudPlan to be retrieved
        :type  plan_id: int

        :return: matching OvercloudPlan, or None if no OvercloudPlan matches
                 the ID
        :rtype:  tuskar_ui.api.tuskar.OvercloudPlan
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
    def delete(cls, request, plan_id):
        """Delete an OvercloudPlan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: plan id
        :type  plan_id: int
        """
        return

    @cached_property
    def role_list(self):
        return [OvercloudRole(role) for role in self.roles]

    def parameter(self, param_name):
        for parameter in self.parameters:
            if parameter['name'] == param_name:
                return parameter

    def parameter_value(self, param_name):
        parameter = self.parameter(param_name)
        if parameter is not None:
            return parameter['value']


class OvercloudRole(base.APIDictWrapper):
    _attrs = ('id', 'name', 'version', 'description', 'created_at')

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud roles"), [])
    def list(cls, request):
        """Return a list of Overcloud Roles in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overcloud Roles, or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.tuskar.OvercloudRole
        """
        roles = TEST_DATA.tuskarclient_roles.list()
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
        :rtype:  tuskar_ui.api.tuskar.OvercloudRole
        """
        for role in OvercloudRole.list(request):
            if role.id == role_id:
                return role

    # TODO(tzumainn): fix this once we know how a role corresponds to
    # its provider resource type
    @property
    def provider_resource_type(self):
        return self.name

    # TODO(tzumainn): fix this once we know how this connection can be
    # made
    @property
    def node_count_parameter_name(self):
        return self.name + 'NodeCount'

    # TODO(tzumainn): fix this once we know how this connection can be
    # made
    @property
    def image_id_parameter_name(self):
        return self.name + 'ImageID'

    # TODO(tzumainn): fix this once we know how this connection can be
    # made
    @property
    def flavor_id_parameter_name(self):
        return self.name + 'FlavorID'
