Setup
=====

This is a quick guide to setting up tuskar-ui.

Prerequisites
-------------

tuskar-ui is a web UI for talking to Tuskar. It is an extension of the
existing Horizon web interface.

Installation prerequisites are:

1. A functional OpenStack installation. Horizon and tuskar-ui will
   connect to the Keystone service here. Keystone does *not* need to be
   on the same machine as your tuskar-ui interface, but its HTTP API
   must be accessible.
2. A functional Tuskar installation. tuskar-ui talks to Tuskar via an
   HTTP interface. It may, but does not have to, reside on the same
   machine as tuskar-ui, but it must be network accessible.

You may find
`the Tuskar install guide <https://github.com/tuskar/tuskar/blob/master/INSTALL.rst>`_
helpful.

For baremetal provisioning, you will want a Nova Baremetal driver
installed and registered in the Keystone services catalog. (You can
`read more about setting up Nova Baremetal here <https://wiki.openstack.org/wiki/Baremetal>`_.)

Installing the packages
-----------------------

tuskar-ui is a Django app written in Python and has a few installation
dependencies:

On a RHEL 6 system, you should install the following:

::

    yum install git python-devel swig openssl-devel mysql-devel libxml2-devel libxslt-devel gcc gcc-c++

The above should work well for similar RPM-based distributions. For
other distros or platforms, you will obviously need to convert as
appropriate.

Then, you'll want to use the ``easy_install`` utility to set up a few
other tools:

::

    easy_install pip
    easy_install nose

You will also want to install Node.js, which is needed by Horizon to
build stylesheets (from LESS).

On Fedora 18+, you can ``yum install nodejs``. (Note that the package
called ``node`` is not related to Node.js.)

On RHEL 6, you'll need to build nodejs from source:

::

    wget http://nodejs.org/dist/v0.10.15/node-v0.10.15.tar.gz
    tar -zxf node-v0.10.15.tar.gz
    cd node-v0.10.15
    ./configure
    make && make install

Install the management UI
-------------------------

Begin by cloning the tuskar-ui repository:

::

    git clone git://github.com/tuskar/tuskar-ui.git

Then, install a virtual environment for your setup:

::

    cd tuskar-ui
    python tools/install_venv.py

Next, run ``run_tests.sh`` to have pip install dependencies:

::

    ./run_tests.sh

Set up your ``local_settings.py`` file:

::

    cp openstack_dashboard/local/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  ``OPENSTACK_HOST`` should be configured with the hostname of your
   OpenStack server. Verify that the ``OPENSTACK_KEYSTONE_URL`` and
   ``OPENSTACK_KEYSTONE_DEFAULT_ROLE`` settings are correct for your
   environment. (They should be correct unless you modified your
   OpenStack server to change them.)
-  ``TUSKAR_ENDPOINT_URL`` should point to the Tuskar server you
   configured. It normally runs on port 6385.
-  ``NOVA_BAREMETAL_CREDS`` is a dictionary of settings for connecting
   to Nova Baremetal. This information is normally gathered from
   Keystone's service catalog, but a common configuration with Tuskar
   and friends is to have Nova Baremetal reachable only from certain
   machines, so the credentials are held separately right now. The
   ``user``, ``password``, and ``tenant`` settings will very likely
   match those of Keystone, and ``auth_url`` may also be the same.
   ``bypass_url`` points directly to the Nova Baremetal API, with the
   last parameter in the URL being your tenant ID.

You can find the tenant ID by running the following from the command
line:

::

    keystone --os-username=USERNAME --os-password=PASSWORD --os-tenant-name=TENANTNAME --os-auth-url=http://AUTHURL:5000/v2.0/ tenant-list

and selecting the id column that matches your tenant name.

(Of course, substituting the appropriate values in for ``USERNAME``,
``PASSWORD``, ``TENANTNAME`` and ``AUTHURL``)

Long-term, this ``NOVA_BAREMETAL_CREDS`` block will likely not be
necessary.

Final setup
-----------

Now that your configuration is in order, it's time to set up a couple
other things.

First, activate your virtual environment:

::

    source .venv/bin/activate

Then, synchronize your local database:

::

    ./manage.py syncdb

Starting the app
----------------

If everything has gone according to plan, you should be able to run:

::

    tools/with_venv.sh ./manage.py runserver

and have the application start on port 8000. The Tuskar dashboard will
be located at http://localhost:8000/infrastructure

If you wish to access it remotely (i.e., not just from localhost), you
need to open port 8000 in iptables:

::

    iptables -I INPUT -p tcp --dport 8000 -j ACCEPT

and launch the server with ``0.0.0.0:8000`` on the end:

::

    tools/with_venv.sh ./manage.py runserver 0.0.0.0:8000

