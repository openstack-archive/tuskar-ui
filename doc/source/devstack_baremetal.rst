Bare Metal configuration in DevStack
------------------------------------

To enable Bare Metal driver in DevStack you need to:

1. Add following settings to ``localrc``::

    VIRT_DRIVER=baremetal
    enable_service baremetal

2. Update ``./lib/baremetal``::

    - BM_DNSMASQ_FROM_NOVA_NETWORK=`trueorfalse False $BM_DNSMASQ_FROM_NOVA_NETWORK`
    + BM_DNSMASQ_FROM_NOVA_NETWORK=`trueorfalse True $BM_DNSMASQ_FROM_NOVA_NETWORK`

See `Bare Metal DevStack documentation <http://devstack.org/lib/baremetal.html>`_
or `baremetal file itself <https://git.openstack.org/cgit/openstack-dev/devstack/blob/master/lib/baremetal>`_
