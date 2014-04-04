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
`the Tuskar install guide <https://github.com/openstack/tuskar/blob/master/docs/INSTALL.rst>`_
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

Go into ``horizon`` and install a virtual environment for your setup::

    cd horizon
    python tools/install_venv.py


Next, run ``run_tests.sh`` to have pip install Horizon dependencies:

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

Install Tuskar-UI with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -r ../tuskar-ui/requirements.txt
    tools/with_venv.sh pip install -e ../tuskar-ui/

And enable it in Horizon::

    cp ../tuskar-ui/_50_tuskar.py.example openstack_dashboard/local/enabled/_50_tuskar.py

Then disable the other dashboards::

    cp ../tuskar-ui/_10_admin.py.example openstack_dashboard/local/enabled/_10_admin.py
    cp ../tuskar-ui/_20_project.py.example openstack_dashboard/local/enabled/_20_project.py


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

