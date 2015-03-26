=========
Tuskar UI
=========

**Tuskar UI** is a user interface for
`Tuskar <https://github.com/openstack/tuskar>`__, a management API for
OpenStack deployments. It is a plugin for `OpenStack
Horizon <https://wiki.openstack.org/wiki/Horizon>`__.

High-Level Overview
-------------------

Tuskar UI endeavours to be a stateless UI, relying on Tuskar API calls
as much as possible. We use existing Horizon libraries and components
where possible. If added libraries and components are needed, we will
work with the OpenStack community to push those changes back into Horizon.

Interested in seeing Tuskar and Tuskar UI in action?
`Watch a demo! <https://www.youtube.com/watch?v=-6whFIqCqLU>`_


Installation Guide
------------------

Use the `Installation Guide <http://tuskar-ui.readthedocs.org/en/latest/install.html>`_ to install Tuskar UI.

Nodes List File
---------------

There is possibility to upload CSV file with given list of nodes.
This file is formatted as::

    driver,address,username,password/ssh key,mac addresses,cpu architecture,number of CPUs,available memory,available storage

License
-------

This project is licensed under the Apache License, version 2. More
information can be found in the LICENSE file.

Contact Us
----------

Join us on IRC (Internet Relay Chat)::

    Network: Freenode (irc.freenode.net/tuskar)
    Channel: #tuskar

Or send an email to openstack-dev@lists.openstack.org.
