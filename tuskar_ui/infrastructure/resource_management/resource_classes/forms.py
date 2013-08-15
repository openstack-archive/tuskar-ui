from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from tuskar_ui import api as tuskar

import logging

LOG = logging.getLogger(__name__)


class DeleteForm(forms.SelfHandlingForm):
    def __init__(self, request, *args, **kwargs):
        super(DeleteForm, self).__init__(request, *args, **kwargs)

        resource_class = self.initial.get('resource_class', None)
        self.command = DeleteCommand(request, resource_class)

    def handle(self, request, data):
        try:
            self.command.execute()

            messages.success(request, self.command.msg)
            return True
        except Exception:
            exceptions.handle(request, _("Unable to delete Resource Class."))


# TODO(this command will be reused in table, so code is not duplicated)
class DeleteCommand(object):
    def __init__(self, request, resource_class):
        self.resource_class = resource_class
        self.request = request
        self.header = (_("Deleting resource class '%s.'")
                       % self.resource_class.name)
        self.msg = ""

    def execute(self):
        try:
            tuskar.ResourceClass.delete(self.request,
                                        self.resource_class.id)
            self.msg = (_('Successfully deleted Class "%s".')
                        % self.resource_class.name)
        except Exception:
            self.msg = _('Failed to delete Class %s') % self.resource_class.id
            LOG.info(self.msg)
            redirect = reverse(
                "horizon:infrastructure:resource_management:index")
            exceptions.handle(self.request, self.msg, redirect=redirect)
