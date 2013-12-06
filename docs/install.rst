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
`the Tuskar install guide <https://github.com/openstack/tuskar/blob/master/INSTALL.rst>`_
helpful.

For baremetal provisioning, you will want a Nova Baremetal driver
installed and registered in the Keystone services catalog. (You can
`read more about setting up Nova Baremetal here <https://wiki.openstack.org/wiki/Baremetal>`_.)

If you are using Devstack to run OpenStack, you can use
`Devstack Baremetal configuration <https://github.com/openstack/tuskar-ui/blob/master/docs/devstack_baremetal.rst>`_.

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

Install the management UI
-------------------------

Begin by cloning the horizon and tuskar-ui repositories:

::

    git clone git://github.com/openstack/horizon.git
    git clone git://github.com/openstack/tuskar-ui.git

Go into horizon and create a symlink to the tuskar-ui code:

::

    cd horizon
    ln -s ../tuskar-ui/tuskar_ui

Then, install a virtual environment for your setup:

::

    python tools/install_venv.py

Next, run ``run_tests.sh`` to have pip install dependencies:

::

    ./run_tests.sh

Set up your ``local_settings.py`` file:

::

    cp ../tuskar-ui/local_settings.py.example openstack_dashboard/local/local_settings.py

Open up the copied ``local_settings.py`` file in your preferred text
editor. You will want to customize several settings:

-  ``OPENSTACK_HOST`` should be configured with the hostname of your
   OpenStack server. Verify that the ``OPENSTACK_KEYSTONE_URL`` and
   ``OPENSTACK_KEYSTONE_DEFAULT_ROLE`` settings are correct for your
   environment. (They should be correct unless you modified your
   OpenStack server to change them.)
-  ``TUSKAR_ENDPOINT_URL`` should point to the Tuskar server you
   configured. It normally runs on port 8585.

Final setup
-----------

Now that your configuration is in order, it's time to set up a couple
other things.

First, activate your virtual environment:

::

    source .venv/bin/activate

tuskar-ui introduces one additional dependency - python-tuskarclient:

::

    pip install git+http://github.com/openstack/python-tuskarclient.git

Starting the app
----------------

If everything has gone according to plan, you should be able to run:

::

    tools/with_venv.sh ./manage.py runserver

and have the application start on port 8080. The Tuskar dashboard will
be located at http://localhost:8080/infrastructure

If you wish to access it remotely (i.e., not just from localhost), you
need to open port 8080 in iptables:

::

    iptables -I INPUT -p tcp --dport 8080 -j ACCEPT

and launch the server with ``0.0.0.0:8080`` on the end:

::

    tools/with_venv.sh ./manage.py runserver 0.0.0.0:8080

