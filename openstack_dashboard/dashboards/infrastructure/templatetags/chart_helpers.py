from django import template
from django.utils import simplejson

register = template.Library()


@register.filter()
def remaining_capacity_by_flavors(obj):
    flavors = obj.list_flavors

    decorated_obj = " ".join(
        [("<p><strong>{0}</strong> {1}</p>").format(
            str(flavor.used_instances),
            flavor.name)
            for flavor in flavors])

    decorated_obj = ("<p>Capacity remaining by flavors: </p>" +
                     decorated_obj)

    return decorated_obj


@register.filter()
def all_used_instances(obj):
    flavors = obj.list_flavors

    all_used_instances_info = []
    for flavor in flavors:
        info = {}
        info['popup_used'] = (
            '<p> {0}% total,'
            ' <strong> {1} instances</strong> of {2}</p>'.format(
            flavor.used_instances,
            flavor.used_instances,
            flavor.name))
        info['used_instances'] = str(flavor.used_instances)

        all_used_instances_info.append(info)

    return simplejson.dumps(all_used_instances_info)
