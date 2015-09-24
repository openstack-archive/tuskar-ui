Contributing
============

The code repository is located at `OpenStack <https://github.com/openstack>`__.
Please go there if you want to check it out:

    git clone https://github.com/openstack/tuskar-ui.git

The list of bugs and blueprints is on Launchpad:

`<https://launchpad.net/tuskar-ui>`__

We use OpenStack's Gerrit for the code contributions:

`<https://review.openstack.org/#/q/status:open+project:openstack/tuskar-ui,n,z>`__

and we follow the `OpenStack Gerrit Workflow <http://docs.openstack.org/infra/manual/developers.html#development-workflow>`__.

If you're interested in the code, here are some key places to start:

* `tuskar_ui/api.py <https://github.com/openstack/tuskar-ui/blob/master/tuskar_ui/api.py>`_
  - This file contains all the API calls made to the Tuskar API
  (through python-tuskarclient).
* `tuskar_ui/infrastructure <https://github.com/openstack/tuskar-ui/tree/master/tuskar_ui/infrastructure>`_
  - The Tuskar UI code is contained within this directory.

Running tests
=============

There are several ways to run tests for tuskar-ui.

Using ``tox``:

    This is the easiest way to run tests. When run, tox installs dependencies,
    prepares the virtual python environment, then runs test commands. The gate
    tests in gerrit usually also use tox to run tests. For available tox
    environments, see ``tox.ini``.

By running ``run_tests.sh``:

    Tests can also be run using the ``run_tests.sh`` script, to see available
    options, run it with the ``--help`` option. It handles preparing the
    virtual environment and executing tests, but in contrast with tox, it does
    not install all dependencies, e.g. ``jshint`` must be installed before
    running the jshint testcase.

Manual tests:

    To manually check tuskar-ui, it is possible to run a development server
    for tuskar-ui by running ``run_tests.sh --runserver``.

    To run the server with the settings used by the test environment:
    ``run_tests.sh --runserver 0.0.0.0:8000 --settings=tuskar_ui.test.settings``

OpenStack Style Commandments
============================

- Step 1: Read http://www.python.org/dev/peps/pep-0008/
- Step 2: Read http://www.python.org/dev/peps/pep-0008/ again
- Step 3: Read https://github.com/openstack-dev/hacking/blob/master/HACKING.rst
