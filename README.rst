tuskar-ui
=========

**tuskar-ui** is a user interface for
`Tuskar </stackforge/tuskar>`__, a management API for
OpenStack deployments. It is a plugin for `OpenStack
Horizon <https://wiki.openstack.org/wiki/Horizon>`__.

High-Level Overview
-------------------

Tuskar-UI endeavours to be a stateless UI, relying on Tuskar API calls 
as much as possible. We use existing Horizon libraries and components 
where possible. If added libraries and components are needed, we will 
work with the OpenStack community to push those changes back into Horizon.

Code Repository
---------------

We've moved the code to `stackforge <https://github.com/stackforge>`__ 
to be more familiar to the OpenStack developers. Please go there if you
want to check it out:

    git clone https://github.com/stackforge/tuskar-ui.git

The list of bugs and blueprints is on Launchpad:

`<https://launchpad.net/tuskar-ui>`__

We use OpenStack's Gerrit for the code contributions:

`<https://review.openstack.org/#/q/status:open+project:stackforge/tuskar-ui,n,z>`__

and we follow the `OpenStack Gerrit Workflow <https://wiki.openstack.org/wiki/Gerrit_Workflow>`__.

Installation Guide
------------------

Use the `Installation Guide </stackforge/tuskar-ui/blob/master/docs/install.rst>`_ to install Tuskar-UI.

License
-------

This project is licensed under the Apache License, version 2. More
information can be found in the LICENSE file.

Further Documentation
---------------------

Check out our `docs directory 
</stackforge/tuskar-ui/blob/master/docs/index.rst>`_
for expanded documentation.

Contact Us
----------

Join us on IRC (Internet Relay Chat)::

    Network: Freenode (irc.freenode.net/tuskar)
    Channel: #tuskar

Or send an email to openstack-dev@lists.openstack.org.
