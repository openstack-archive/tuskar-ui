Contributing
------------

The code repository is located at `OpenStack <https://github.com/openstack>`__.
Please go there if you want to check it out:

    git clone https://github.com/openstack/tuskar-ui.git

The list of bugs and blueprints is on Launchpad:

`<https://launchpad.net/tuskar-ui>`__

We use OpenStack's Gerrit for the code contributions:

`<https://review.openstack.org/#/q/status:open+project:openstack/tuskar-ui,n,z>`__

and we follow the `OpenStack Gerrit Workflow <https://wiki.openstack.org/wiki/Gerrit_Workflow>`__.

If you're interested in the code, here are some key places to start:

* `tuskar_ui/api.py <https://github.com/openstack/tuskar-ui/blob/master/tuskar_ui/api.py>`_
  - This file contains all the API calls made to the Tuskar API
  (through python-tuskarclient).
* `tuskar_ui/infrastructure <https://github.com/openstack/tuskar-ui/tree/master/tuskar_ui/infrastructure>`_
  - The Tuskar UI code is contained within this directory.

OpenStack Style Commandments
============================

- Step 1: Read http://www.python.org/dev/peps/pep-0008/
- Step 2: Read http://www.python.org/dev/peps/pep-0008/ again
- Step 3: Read https://github.com/openstack-dev/hacking/blob/master/HACKING.rst
