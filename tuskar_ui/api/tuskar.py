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
from openstack_dashboard.api import glance
from tuskarclient import client as tuskar_client

from tuskar_ui.api import flavor
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa

LOG = logging.getLogger(__name__)
TUSKAR_ENDPOINT_URL = getattr(django.conf.settings, 'TUSKAR_ENDPOINT_URL')


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
def tuskarclient(request):
    c = tuskar_client.get_client('2', tuskar_url=TUSKAR_ENDPOINT_URL,
                                 os_auth_token=request.user.token.id)
    return c


class OvercloudPlan(base.APIResourceWrapper):
    _attrs = ('id', 'name', 'description', 'created_at', 'modified_at',
              'roles', 'parameters', 'template')

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
        plan = tuskarclient(request).plans.create(name=name,
                                                  description=description)
        return cls(plan, request=request)

    @classmethod
    def patch(cls, request, plan_id, name, description):
        """Update an OvercloudPlan in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: id of the plan we want to update
        :type  plan_id: string

        :param name: plan name
        :type  name: string

        :param description: plan description
        :type  description: string

        :return: the updated OvercloudPlan object
        :rtype:  tuskar_ui.api.tuskar.OvercloudPlan
        """
        plan = tuskarclient(request).plans.patch(plan_uuid=plan_id,
                                                 name=name,
                                                 description=description)
        return cls(plan, request=request)

    @classmethod
    def list(cls, request):
        """Return a list of OvercloudPlans in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of OvercloudPlans, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.tuskar.OvercloudPlan
        """
        plans = tuskarclient(request).plans.list()
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
        plan = tuskarclient(request).plans.get(plan_uuid=plan_id)
        return cls(plan, request=request)

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
            return plan
        # if plan doesn't exist, create it
        plan = cls.create(request, 'overcloud', 'overcloud')
        return plan

    @classmethod
    def delete(cls, request, plan_id):
        """Delete an OvercloudPlan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: plan id
        :type  plan_id: int
        """
        tuskarclient(request).plans.delete(plan_uuid=plan_id)

    @cached_property
    def role_list(self):
        return [OvercloudRole.get(self._request, role['uuid'])
                for role in self.roles]

    def parameter_list(self, include_key_parameters=True):
        params = self.parameters
        if not include_key_parameters:
            key_params = []
            for role in self.role_list:
                key_params.extend([role.node_count_parameter_name,
                                   role.image_id_parameter_name,
                                   role.flavor_id_parameter_name])
            params = [p for p in params if p['name'] not in key_params]
        return params

    def parameter(self, param_name):
        for parameter in self.parameters:
            if parameter['name'] == param_name:
                return parameter

    def parameter_value(self, param_name, default=None):
        parameter = self.parameter(param_name)
        if parameter is not None:
            return parameter['value']
        return default


class OvercloudRole(base.APIResourceWrapper):
    _attrs = ('uuid', 'name', 'version', 'description', 'created')

    def __init__(self, apiresource, request=None):
        super(OvercloudRole, self).__init__(apiresource)
        self._request = request

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
        roles = tuskarclient(request).roles.list()
        return [cls(role, request=request) for role in roles]

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
            if role.uuid == role_id:
                return role

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get_by_image(cls, request, plan, image):
        """Return the Tuskar OvercloudRole whose ImageID
        parameter matches the passed in image

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan: associated plan to check against
        :type  plan: OvercloudPlan

        :param image: image to be matched
        :type  image: Image

        :return: matching OvercloudRole, or None if no matching
                 OvercloudRole can be found
        :rtype:  tuskar_ui.api.tuskar.OvercloudRole
        """
        for role in OvercloudRole.list(request):
            image_id_from_plan = plan.parameter_value(
                role.image_id_parameter_name)
            if image_id_from_plan == image.id:
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

    def image(self, plan):
        image_id = plan.parameter_value(self.image_id_parameter_name)
        if image_id:
            return glance.image_get(self._request, image_id)

    def flavor(self, plan):
        flavor_id = plan.parameter_value(self.flavor_id_parameter_name)
        if flavor_id:
            return flavor.Flavor.get(self._request, flavor_id)

    @property
    def id(self):
        return self.uuid
