=========
Tuskar-UI
=========

Tuskar-UI is a user interface for `Tuskar <https://github.com/tuskar/tuskar>`_, a management API for OpenStack deployments.  It is based on (and forked from) `OpenStack Horizon <https://wiki.openstack.org/wiki/Horizon>`_.

High-Level Overview
-------------------

Tuskar-UI endeavours to be a stateless UI, relying on Tuskar API calls as much as possible.  We use existing Horizon libraries and components where possible.  If added libraries and components are needed, we will work with the OpenStack community to push those changes back into Horizon.

Interested in seeing Tuskar and Tuskar-UI in action? `Watch a demo! <https://www.youtube.com/watch?v=VEY035-Lyzo>`_


Developer Information
---------------------

Install and Contribute
~~~~~~~~~~~~~~~~~~~~~~

Follow the `Installation Guide <https://github.com/tuskar/tuskar-ui/blob/master/docs/install.md>`_ to install Tuskar-UI.

If you're interested in the code, here are some key places to start:

* `openstack_dashboard/api/tuskar.py <https://github.com/tuskar/tuskar-ui/blob/master/openstack_dashboard/api/tuskar.py>`_ - This file contains all the API calls made to the Tuskar API (through python-tuskarclient).
* `openstack_dashboard/dashboards/infrastructure <https://github.com/tuskar/tuskar-ui/tree/master/openstack_dashboard/dashboards/infrastructure>`_ - The Tuskar UI code is contained within this directory.  Up to this point, UI development has been focused within the resource_management/ subdirectory.

*TODO* Contribution Guide

Future Work
-----------

Contact Us
----------

Join us on IRC (Internet Relay Chat)::

    Network: Freenode (irc.freenode.net/tuskar)
    Channel: #tuskar
