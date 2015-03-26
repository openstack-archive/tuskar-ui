==========
User Guide
==========

Nodes List File
---------------

To allow users to load a bunch of nodes at once, there is possibility to
upload CSV file with given list of nodes. This file should be formatted as

::

    driver,address,username,password/ssh key,mac addresses,cpu architecture,number of CPUs,available memory,available storage

Even if there is no all data available, we assume empty values for missing
keys and trying to parse everything, what is possible.
