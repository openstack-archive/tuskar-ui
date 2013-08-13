=========
Tuskar-UI
=========

Tuskar-UI is a user interface for `Tuskar <https://github.com/stackforge/tuskar>`_, a management API for OpenStack deployments.  It is a plugin for `OpenStack Horizon <https://wiki.openstack.org/wiki/Horizon>`_.

High-Level Overview
-------------------

Tuskar-UI endeavours to be a stateless UI, relying on Tuskar API calls as much as possible.  We use existing Horizon libraries and components where possible.  If added libraries and components are needed, we will work with the OpenStack community to push those changes back into Horizon.

Interested in seeing Tuskar and Tuskar-UI in action? `Watch a demo! <https://www.youtube.com/watch?v=VEY035-Lyzo>`_


Developer Information
---------------------

Installation Guide
~~~~~~~~~~~~~~~~~~

Follow the `Installation Guide <https://github.com/stackforge/tuskar-ui/blob/master/docs/install.rst>`_ to install Tuskar-UI.

Contributing
~~~~~~~~~~~~

We've moved the code to `stackforge <https://github.com/stackforge>`__ 
to be more familiar to the OpenStack developers. Please go there if you
want to check it out:

    git clone https://github.com/stackforge/tuskar-ui.git

The list of bugs and blueprints is on Launchpad:

`<https://launchpad.net/tuskar-ui>`__

We use OpenStack's Gerrit for the code contributions:

`<https://review.openstack.org/#/q/status:open+project:stackforge/tuskar-ui,n,z>`__

and we follow the `OpenStack Gerrit Workflow <https://wiki.openstack.org/wiki/Gerrit_Workflow>`__.

If you're interested in the code, here are some key places to start:

* `tuskar_ui/api.py <https://github.com/stackforge/tuskar-ui/blob/master/tuskar_ui/api.py>`_ - This file contains all the API calls made to the Tuskar API (through python-tuskarclient).
* `tuskar_ui/infrastructure <https://github.com/stackforge/tuskar-ui/tree/master/tuskar_ui/infrastructure>`_ - The Tuskar UI code is contained within this directory.  Up to this point, UI development has been focused within the resource_management/ subdirectory.

Future Work
-----------

Contact Us
----------

Join us on IRC (Internet Relay Chat)::

    Network: Freenode (irc.freenode.net/tuskar)
    Channel: #tuskar

Or send an email to openstack-dev@lists.openstack.org.
