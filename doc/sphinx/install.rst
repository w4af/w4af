Installation
============

Prerequisites
-------------

Make sure you have the following software ready before starting the installation:

 * Git client: ``sudo apt-get install git``
 * Python 3.11, which is installed by default in most systems
 * Pip version 23.x: ``sudo apt-get install python3-pip``
 * node-js
 * Optional: If you want python3 to launch when typing python: ``sudo apt-get install python-is-python``

Installation
------------

.. code-block:: bash

    git clone https://github.com/w4af/w4af.git
    cd w4af/
    python -m pip install --upgrade pipenv wheel
    pipenv install
    npm install
    pipenv shell
    ./w4af_console

Let me explain what's going on there:

 * First we use ``git`` to download ``w4af``'s source code
 * Then we install pipenv and wheel
 * Dependencies are installed by running ``pipenv install`` and ``npm install``
 * virtual environment is started with ``pipenv shell``

The framework dependencies don't change too often, but don't be alarmed if after
updating your installation ``w4af`` requires you to install new dependencies via the above commands

Supported platforms
-------------------

The framework should work on all Python supported platforms.

.. note::

   The platform used for development is Ubuntu 22.04 and running our continuous integration tests
   is Ubuntu 22.04 LTS.

.. warning::

   While in theory you can install w4af in Microsoft Windows or Mac OS, we don't recommend
   nor support that installation process.

Installing using Docker
-----------------------

`Docker <https://www.docker.com/>`_ is awesome, it allows users to run ``w4af``
without installing any of it's dependencies. The only pre-requisite is to
`install docker <http://docs.docker.com/installation/>`_ , which is widely
supported.

Once the docker installation is running these steps will yield a running
``w4af`` console:

.. code-block:: console

    docker run -it w4af/w4af:latest

For advanced usage of ``w4af``'s docker container please see Readme in subfolder extras/docker of the w4af-repo.

Troubleshooting
---------------

After running the helper script w4af still says I have missing python dependencies, what should I do?
_____________________________________________________________________________________________________

You will recognize this when this message appears: "Your python installation
needs the following modules to run w4af".

First you'll want to check that all the dependencies are installed. To do that
just follow these steps:

.. code-block:: console

    $ cd w4af
    $ ./w4af_console
    ...
    Your python installation needs the following modules to run w4af:
    futures
    ...
    $ pip freeze | grep futures
    futures==2.1.5
    $

TODO: Needs to be reworked: Replace ``futures`` with the library that is missing in your system. If the
``pip freeze | grep futures`` command returns an empty result, you'll need to
install the dependency using the ``/tmp/w4af_dependency_install.sh`` command.
Pay special attention to the output of that command, if installation fails
you won't be able to run ``w4af``.

..
	It is important to notice that ``w4af`` requires specific versions of the third-party libraries. The specific versions required at ``/tmp/w4af_dependency_install.sh`` need to match the ones you see in the output of ``pip freeze``. If the versions don't match you can always install a specific version using ``pip install --upgrade futures==2.1.5``.


How do I ask for support on installation issues?
________________________________________________

You can `create a ticket <https://github.com/w4af/w4af/issues/new>`_
containing the following information:

 * Your linux distribution (usually the contents of ``/etc/lsb-release`` will be enough)
 * The output of ``pip freeze``
 * The output of ``python --version``
