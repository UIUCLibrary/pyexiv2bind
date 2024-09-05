Py3exiv2bind
============

.. image:: https://img.shields.io/badge/License-UIUC%20License-green.svg?label=License
    :target: https://otm.illinois.edu/disclose-protect/illinois-open-source-license

.. image:: https://jenkins-prod.library.illinois.edu/buildStatus/icon?job=open+source%2Fpyexiv2bind2%2Fmaster
    :target: https://jenkins-prod.library.illinois.edu/job/open%20source/job/pyexiv2bind2/job/master/

Python binding for exiv2.


Building Portable Python Wheels For Mac
---------------------------------------

Since this package links to C and C++ libraries, to make sure that these files are generated in a portable manner and
will run on other machines, please use the included shell script (contrib/build_mac_wheel.sh) provided to generate
them.


.. code-block:: console

    ./contrib/build_mac_wheel.sh .
