Installation instructions
=========================

Note
----

If you want to install and configure the entire TripleO + Tuskar + Tuskar UI
stack, you can use
`the devtest installation guide <https://wiki.openstack.org/wiki/Tuskar/Devtest>`_.

Otherwise, you can use the installation instructions for Tuskar UI below.

Prerequisites
-------------

Installation prerequisites are:

1. A functional OpenStack installation. Horizon and Tuskar UI will
   connect to the Keystone service here. Keystone does *not* need to be
   on the same machine as your Tuskar UI interface, but its HTTP API
   must be accessible.
2. A functional Tuskar installation. Tuskar UI talks to Tuskar via an
   HTTP interface. It may, but does not have to, reside on the same
   machine as Tuskar UI, but it must be network accessible.

You may find
`the Tuskar install guide <https://github.com/openstack/tuskar/blob/master/doc/source/install.rst>`_
helpful.


Installing the packages
-----------------------

Tuskar UI is a Django app written in Python and has a few installation
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

Begin by cloning the Horizon and Tuskar UI repositories:

::

    git clone git://github.com/openstack/horizon.git
    git clone git://github.com/openstack/python-tuskarclient.git
    git clone git://github.com/openstack/tuskar-ui.git

Go into ``horizon`` and install a virtual environment for your setup::

    cd horizon
    python tools/install_venv.py


Next, run ``run_tests.sh`` to have pip install Horizon dependencies:

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

Install Tuskar UI with all dependencies in your virtual environment::

    tools/with_venv.sh pip install -e ../python-tuskarclient/
    tools/with_venv.sh pip install -e ../tuskar-ui/

And enable it in Horizon::

    cp ../tuskar-ui/_50_tuskar.py.example openstack_dashboard/local/enabled/_50_tuskar.py

Then disable the other dashboards::

    cp ../tuskar-ui/_10_admin.py.example openstack_dashboard/local/enabled/_10_admin.py
    cp ../tuskar-ui/_20_project.py.example openstack_dashboard/local/enabled/_20_project.py
    cp ../tuskar-ui/_30_identity.py.example openstack_dashboard/local/enabled/_30_identity.py


Starting the app
----------------

If everything has gone according to plan, you should be able to run:

::

    tools/with_venv.sh ./manage.py runserver

and have the application start on port 8080. The Tuskar UI dashboard will
be located at http://localhost:8080/infrastructure

If you wish to access it remotely (i.e., not just from localhost), you
need to open port 8080 in iptables:

::

    iptables -I INPUT -p tcp --dport 8080 -j ACCEPT

and launch the server with ``0.0.0.0:8080`` on the end:

::

    tools/with_venv.sh ./manage.py runserver 0.0.0.0:8080

