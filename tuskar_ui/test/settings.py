import os

from django.utils.translation import ugettext_lazy as _

from horizon.test.settings import *  # noqa
from horizon.utils.secret_key import generate_or_read_from_file

from tuskar_ui.exceptions import NOT_FOUND
from tuskar_ui.exceptions import RECOVERABLE
from tuskar_ui.exceptions import UNAUTHORIZED


TEST_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(TEST_DIR, ".."))

SECRET_KEY = generate_or_read_from_file(os.path.join(TEST_DIR,
                                                     '.secret_key_store'))
ROOT_URLCONF = 'openstack_dashboard.urls'
TEMPLATE_DIRS = (
    os.path.join(TEST_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'openstack_dashboard.context_processors.openstack',
)

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django_nose',
    'openstack_auth',
    'compressor',
    'horizon',
    'openstack_dashboard',
    'openstack_dashboard.dashboards.project',
    'openstack_dashboard.dashboards.admin',
    'tuskar_ui.infrastructure',
    'openstack_dashboard.dashboards.settings',
)

AUTHENTICATION_BACKENDS = ('openstack_auth.backend.KeystoneBackend',)

SITE_BRANDING = 'OpenStack'

HORIZON_CONFIG = {
    'dashboards': ('project', 'admin', 'infrastructure', 'settings'),
    'default_dashboard': 'project',
    "password_validator": {
        "regex": '^.{8,18}$',
        "help_text": _("Password must be between 8 and 18 characters.")
    },
    'user_home': None,
    'help_url': "http://docs.openstack.org",
    'exceptions': {'recoverable': RECOVERABLE,
                   'not_found': NOT_FOUND,
                   'unauthorized': UNAUTHORIZED},
}

# Set to True to allow users to upload images to glance via Horizon server.
# When enabled, a file form field will appear on the create image form.
# See documentation for deployment considerations.
HORIZON_IMAGES_ALLOW_UPLOAD = True

AVAILABLE_REGIONS = [
    ('http://localhost:5000/v2.0', 'local'),
    ('http://remote:5000/v2.0', 'remote'),
]

OPENSTACK_KEYSTONE_URL = "http://localhost:5000/v2.0"
OPENSTACK_KEYSTONE_DEFAULT_ROLE = "Member"

OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT = True
OPENSTACK_KEYSTONE_DEFAULT_DOMAIN = 'test_domain'

OPENSTACK_KEYSTONE_BACKEND = {
    'name': 'native',
    'can_edit_user': True,
    'can_edit_group': True,
    'can_edit_project': True,
    'can_edit_domain': True,
    'can_edit_role': True
}

OPENSTACK_NEUTRON_NETWORK = {
    'enable_lb': True
}

OPENSTACK_HYPERVISOR_FEATURES = {
    'can_set_mount_point': True,

    # NOTE: as of Grizzly this is not yet supported in Nova so enabling this
    # setting will not do anything useful
    'can_encrypt_volumes': False
}

LOGGING['loggers']['openstack_dashboard'] = {
    'handlers': ['test'],
    'propagate': False,
}

SECURITY_GROUP_RULES = {
    'all_tcp': {
        'name': 'ALL TCP',
        'ip_protocol': 'tcp',
        'from_port': '1',
        'to_port': '65535',
    },
    'http': {
        'name': 'HTTP',
        'ip_protocol': 'tcp',
        'from_port': '80',
        'to_port': '80',
    },
}

NOSE_ARGS = ['--nocapture',
             '--nologcapture',
             '--cover-package=openstack_dashboard',
             '--cover-inclusive',
             '--all-modules']

TUSKAR_ENDPOINT_URL = "http://127.0.0.1:6385"

OVERCLOUD_CREDS = {
    'enabled': True,
    'user': 'admin',
    'password': 'password',
    'tenant': 'admin',
    'auth_url': 'http://localhost:5000/v2.0/',
}
