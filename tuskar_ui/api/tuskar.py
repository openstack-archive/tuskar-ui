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

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.api import base
from openstack_dashboard.api import glance
from tuskarclient import client as tuskar_client

from tuskar_ui.api import flavor
from tuskar_ui.cached_property import cached_property  # noqa
from tuskar_ui.handle_errors import handle_errors  # noqa

LOG = logging.getLogger(__name__)
MASTER_TEMPLATE_NAME = 'plan.yaml'
ENVIRONMENT_NAME = 'environment.yaml'
TUSKAR_SERVICE = 'management'


# FIXME: request isn't used right in the tuskar client right now,
# but looking at other clients, it seems like it will be in the future
def tuskarclient(request, password=None):
    api_version = "2"
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    ca_file = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    endpoint = base.url_for(request, TUSKAR_SERVICE)

    LOG.debug('tuskarclient connection created using token "%s" and url "%s"' %
              (request.user.token.id, endpoint))

    client = tuskar_client.get_client(api_version,
                                      tuskar_url=endpoint,
                                      insecure=insecure,
                                      ca_file=ca_file,
                                      username=request.user.username,
                                      password=password,
                                      os_auth_token=request.user.token.id)
    return client


class Plan(base.APIResourceWrapper):
    _attrs = ('uuid', 'name', 'description', 'created_at', 'modified_at',
              'roles', 'parameters')

    def __init__(self, apiresource, request=None):
        super(Plan, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, name, description):
        """Create a Plan in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param name: plan name
        :type  name: string

        :param description: plan description
        :type  description: string

        :return: the created Plan object
        :rtype:  tuskar_ui.api.tuskar.Plan
        """
        plan = tuskarclient(request).plans.create(name=name,
                                                  description=description)
        return cls(plan, request=request)

    @classmethod
    def patch(cls, request, plan_id, parameters):
        """Update a Plan in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: id of the plan we want to update
        :type  plan_id: string

        :param parameters: new values for the plan's parameters
        :type  parameters: dict

        :return: the updated Plan object
        :rtype:  tuskar_ui.api.tuskar.Plan
        """
        parameter_list = [{
            'name': unicode(name),
            'value': unicode(value),
        } for (name, value) in parameters.items()]
        plan = tuskarclient(request).plans.patch(plan_id, parameter_list)
        return cls(plan, request=request)

    @classmethod
    def list(cls, request):
        """Return a list of Plans in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Plans, or an empty list if there are none
        :rtype:  list of tuskar_ui.api.tuskar.Plan
        """
        plans = tuskarclient(request).plans.list()
        return [cls(plan, request=request) for plan in plans]

    @classmethod
    @handle_errors(_("Unable to retrieve plan"))
    def get(cls, request, plan_id):
        """Return the Plan that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: id of Plan to be retrieved
        :type  plan_id: int

        :return: matching Plan, or None if no Plan matches
                 the ID
        :rtype:  tuskar_ui.api.tuskar.Plan
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
        """Delete a Plan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan_id: plan id
        :type  plan_id: int
        """
        tuskarclient(request).plans.delete(plan_uuid=plan_id)

    @cached_property
    def role_list(self):
        return [Role.get(self._request, role.uuid)
                for role in self.roles]

    @cached_property
    def _roles_by_name(self):
        return dict((role.name, role) for role in self.role_list)

    def get_role_by_name(self, role_name):
        """Get the role with the given name."""
        return self._roles_by_name[role_name]

    def get_role_node_count(self, role):
        """Get the node count for the given role."""
        return int(self.parameter_value(role.node_count_parameter_name,
                                        0) or 0)

    @cached_property
    def templates(self):
        return tuskarclient(self._request).plans.templates(self.uuid)

    @cached_property
    def master_template(self):
        return self.templates.get(MASTER_TEMPLATE_NAME, '')

    @cached_property
    def environment(self):
        return self.templates.get(ENVIRONMENT_NAME, '')

    @cached_property
    def provider_resource_templates(self):
        template_dict = dict(self.templates)
        del template_dict[MASTER_TEMPLATE_NAME]
        del template_dict[ENVIRONMENT_NAME]
        return template_dict

    def parameter_list(self, include_key_parameters=True):
        params = self.parameters
        if not include_key_parameters:
            key_params = []
            for role in self.role_list:
                key_params.extend([role.node_count_parameter_name,
                                   role.image_id_parameter_name,
                                   role.flavor_parameter_name])
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

    @property
    def id(self):
        return self.uuid


class Role(base.APIResourceWrapper):
    _attrs = ('uuid', 'name', 'version', 'description', 'created')

    def __init__(self, apiresource, request=None):
        super(Role, self).__init__(apiresource)
        self._request = request

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud roles"), [])
    def list(cls, request):
        """Return a list of Overcloud Roles in Tuskar

        :param request: request object
        :type  request: django.http.HttpRequest

        :return: list of Overcloud Roles, or an empty list if there
                 are none
        :rtype:  list of tuskar_ui.api.tuskar.Role
        """
        roles = tuskarclient(request).roles.list()
        return [cls(role, request=request) for role in roles]

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get(cls, request, role_id):
        """Return the Tuskar Role that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param role_id: ID of Role to be retrieved
        :type  role_id: int

        :return: matching Role, or None if no matching
                 Role can be found
        :rtype:  tuskar_ui.api.tuskar.Role
        """
        for role in Role.list(request):
            if role.uuid == role_id:
                return role

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get_by_image(cls, request, plan, image):
        """Return the Tuskar Role whose ImageID
        parameter matches the passed in image

        :param request: request object
        :type  request: django.http.HttpRequest

        :param plan: associated plan to check against
        :type  plan: Plan

        :param image: image to be matched
        :type  image: Image

        :return: matching Role, or None if no matching
                 Role can be found
        :rtype:  tuskar_ui.api.tuskar.Role
        """
        for role in Role.list(request):
            image_id_from_plan = plan.parameter_value(
                role.image_id_parameter_name)
            if image_id_from_plan == image.id:
                return role

    @classmethod
    @handle_errors(_("Unable to retrieve overcloud role"))
    def get_by_resource_type(cls, request, resource_type):
        for role in Role.list(request):
            if role.provider_resource_type == resource_type:
                return role

    @property
    def provider_resource_type(self):
        return "Tuskar::{0}-{1}".format(self.name, self.version)

    @property
    def provider_resource_group_name(self):
        return "{0}-{1}-resource-servers".format(self.name, self.version)

    @property
    def parameter_prefix(self):
        return "{0}-{1}::".format(self.name, self.version)

    @property
    def node_count_parameter_name(self):
        return self.parameter_prefix + 'count'

    @property
    def image_id_parameter_name(self):
        return self.parameter_prefix + 'Image'

    @property
    def flavor_parameter_name(self):
        return self.parameter_prefix + 'Flavor'

    def image(self, plan):
        image_id = plan.parameter_value(self.image_id_parameter_name)
        if image_id:
            return glance.image_get(self._request, image_id)

    def flavor(self, plan):
        flavor_name = plan.parameter_value(
            self.flavor_parameter_name)
        if flavor_name:
            return flavor.Flavor.get_by_name(self._request, flavor_name)

    @property
    def id(self):
        return self.uuid
