.. Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
.. For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

.. _install:

============
Installation
============

.. :history: 20100725T225600, new for 3.4.
.. :history: 20100820T151500, updated for 3.4b1.
.. :history: 20100906T134800, updated for 3.4b2.
.. :history: 20110604T213400, updated for 3.5b1.
.. :history: 20110629T082400, updated for 3.5.
.. :history: 20110923T081900, updated for 3.5.1.
.. :history: 20120429T162500, updated for 3.5.2b1.
.. :history: 20120503T234000, updated for 3.5.2.
.. :history: 20120929T093600, updated for 3.5.3.
.. :history: 20121117T095000, Now setuptools is a pre-req.
.. :history: 20121128T203000, updated for 3.6b1.
.. :history: 20121223T180800, updated for 3.6b2.
.. :history: 20121229T112400, updated for 3.6b3.
.. :history: 20130105T174400, updated for 3.6.
.. :history: 20131005T210600, updated for 3.7.
.. :history: 20131212T213500, updated for 3.7.1.
.. :history: 20140927T102700, updated for 4.0a1.


.. highlight:: console

.. _coverage_pypi: http://pypi.python.org/pypi/coverage
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _Distribute: http://packages.python.org/distribute/


Installing coverage.py is done in the usual ways. The simplest way is with
pip::

    $ pip install coverage

.. ifconfig:: prerelease

    To install a pre-release version, you will need to specify ``--pre``::

        $ pip install --pre coverage


The alternate old-school technique is:

#.  Install (or already have installed) `setuptools`_ or `Distribute`_.

#.  Download the appropriate kit from the
    `coverage.py page on the Python Package Index`__.

#.  Run ``python setup.py install``.

.. __: coverage_pypi_


Installing from source
----------------------

Coverage.py includes a C extension for speed. If you are installing from
source, you may need to install the python-dev support files, for example
with::

    $ sudo apt-get install python-dev

or for Python 3.x::

    $ sudo apt-get install python3-dev


Installing on Windows
---------------------

For Windows, kits are provided on the `PyPI page`__ for different versions of
Python and different CPU architectures. These kits require that `setuptools`_
be installed as a pre-requisite, but otherwise are self-contained.  They have
the C extension pre-compiled so there's no need to worry about compilers.

.. __: coverage_pypi_


Checking the installation
-------------------------

If all went well, you should be able to open a command prompt, and see
coverage.py installed properly:

.. ifconfig:: not prerelease

    .. parsed-literal::

        $ coverage --version
        Coverage.py, version |release|.
        Documentation at https://coverage.readthedocs.org

.. ifconfig:: prerelease

    .. parsed-literal::

        $ coverage --version
        Coverage.py, version |release|.
        Documentation at https://coverage.readthedocs.org/en/|release|

You can also invoke coverage.py as a module:

.. ifconfig:: not prerelease

    .. parsed-literal::

        $ python -m coverage --version
        Coverage.py, version |release|.
        Documentation at https://coverage.readthedocs.org

.. ifconfig:: prerelease

    .. parsed-literal::

        $ python -m coverage --version
        Coverage.py, version |release|.
        Documentation at https://coverage.readthedocs.org/en/|release|
