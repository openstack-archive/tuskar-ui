# -*- coding: utf8 -*-
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
import django.forms
from django.utils.translation import ugettext_lazy as _
import horizon.workflows

from tuskar_ui import utils

# TODO(rdopieralski) Get this from the Heat template.
TEMPLATE_DATA = {
    "Description": ("Nova API,Keystone,Heat Engine and API,Glance,Neutron,"
                    "Dedicated MySQL server,Dedicated RabbitMQ Server,"
                    "Group of Nova Computes,"
                    "ssl-source: SSL endpoint metadata for openstack,"
                    "Swift-common: OpenStack object storage common "
                    "configurations"),

    "Parameters": {
        "NeutronPublicInterfaceRawDevice": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("If set, the public interface is a vlan with this "
                            "device as the raw device."),
        },
        "HeatPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the Heat service account, used "
                            "by the Heat services.")
        },
        "NovaComputeDriver": {
            "Default": "libvirt.LibvirtDriver",
            "Type": "String",
            "NoEcho": "false",
            "Description": ""
        },
        "NeutronPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the neutron service account, "
                            "used by neutron agents."),
        },
        "NeutronBridgeMappings": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": "The OVS logical->physical bridge mappings to use.",
        },
        "NeutronPublicInterfaceDefaultRoute": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("A custom default route for the "
                            "NeutronPublicInterface."),
        },
        "NeutronDnsmasqOptions": {
            "Default": "dhcp-option-force=26,1400",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("Dnsmasq options for neutron-dhcp-agent."),
        },
        "GlancePassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the glance service account, "
                            "used by the glance services."),
        },
        "GlanceLogFile": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("The filepath of the file to use for logging "
                            "messages from Glance."),
        },
        "notcomputeImage": {
            "Default": "overcloud-control",
            "Type": "String",
            "NoEcho": "false",
            "Description": "",
        },
        "NovaImage": {
            "Default": "overcloud-compute",
            "Type": "String",
            "NoEcho": "false",
            "Description": ""
        },
        "SSLKey": {
            "Default": "",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("If set, the contents of an SSL certificate .key "
                            "file for encrypting SSL endpoints."),
        },
        "KeyName": {
            "Default": "default",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("Name of an existing EC2 KeyPair to enable SSH "
                            "access to the instances"),
        },
        "CeilometerPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": "The password for the ceilometer service account.",
        },
        "NtpServer": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": "",
        },
        "CinderPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the cinder service account, "
                            "used by cinder-api."),
        },
        "ImageUpdatePolicy": {
            "Default": "REPLACE",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("What policy to use when reconstructing "
                            "instances. REBUILD for rebuilds, "
                            "REBUILD_PRESERVE_EPHEMERAL to preserve /mnt."),
        },
        "NeutronPublicInterface": {
            "Default": "eth0",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("What interface to bridge onto br-ex for network "
                            "nodes."),
        },
        "NovaPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the nova service account, used "
                            "by nova-api."),
        },
        "AdminToken": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": "The keystone auth secret."
        },
        "NovaComputeLibvirtType": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": "",
        },
        "NeutronPublicInterfaceIP": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("A custom IP address to put onto the "
                            "NeutronPublicInterface."),
        },
        "SwiftHashSuffix": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("A random string to be used as a salt when "
                            "hashing to determine mappings in the ring."),
        },
        "AdminPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the keystone admin account, "
                            "used for monitoring, querying neutron etc."),
        },
        "CeilometerComputeAgent": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("Indicates whether the Compute agent is present "
                            "and expects nova-compute to be configured "
                            "accordingly"),
            "AllowedValues": ["", "Present"],
        },
        "NeutronFlatNetworks": {
            "Default": "",
            "Type": "String",
            "NoEcho": "false",
            "Description": ("If set, flat networks to configure in neutron "
                            "plugins."),
        },
        "SwiftPassword": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("The password for the swift service account, "
                            "used by the swift proxy services."),
        },
        "CeilometerMeteringSecret": {
            "Default": "unset",
            "Type": "String",
            "NoEcho": "true",
            "Description": "Secret shared by the ceilometer services.",
        },
        "SSLCertificate": {
            "Default": "",
            "Type": "String",
            "NoEcho": "true",
            "Description": ("If set, the contents of an SSL certificate .crt "
                            "file for encrypting SSL endpoints."),
        },
        "Flavor": {
            "Default": "baremetal",
            "Type": "String",
            "NoEcho": "false",
            "Description": "Flavor to request when deploying.",
        },
    },
}


def make_field(name, Type, NoEcho, Default, Description, AllowedValues=None,
               **kwargs):
    """Create a form field using the parameters from a Heat template."""

    label = utils.de_camel_case(name)
    Widget = django.forms.TextInput
    attrs = {}
    widget_kwargs = {}
    if Default == 'unset':
        Default = None
        attrs['placeholder'] = _("auto-generate")
    if Type == 'String':
        Field = django.forms.CharField
    elif Type == 'Integer':
        Field = django.forms.IntegerField
    else:
        raise ValueError("Unsupported parameter type in Heat template.")
    if NoEcho == 'true':
        Widget = django.forms.PasswordInput
        widget_kwargs['render_value'] = True
    if AllowedValues is not None:
        return django.forms.ChoiceField(initial=Default, choices=[
            (value, value) for value in AllowedValues
        ], help_text=Description, required=False, label=label)
    return Field(widget=Widget(attrs=attrs, **widget_kwargs), initial=Default,
                 help_text=Description, required=False, label=label)


class Action(horizon.workflows.Action):
    class Meta:
        slug = 'deployed_configuration'
        name = _("Configuration")

    def __init__(self, *args, **kwargs):
        super(Action, self).__init__(*args, **kwargs)
        parameters = TEMPLATE_DATA['Parameters'].items()
        parameters.sort()
        for name, data in parameters:
            self.fields[name] = make_field(name, **data)


class Step(horizon.workflows.Step):
    action_class = Action
    contributes = ('configuration',)
    template_name = 'infrastructure/overcloud/undeployed_configuration.html'

    def contribute(self, data, context):
        context['configuration'] = data
        return context
