Installation
============

Prerequisites
-------------

Make sure you have the following software ready before starting the installation:

 * Git client: ``sudo apt-get install git``
 * Python 2.7, which is installed by default in most systems
 * Pip version 1.1: ``sudo apt-get install python-pip``

Installation
------------

.. code-block:: bash

    git clone https://github.com/andresriancho/w4af.git
    cd w4af/
    ./w4af_console
    . /tmp/w4af_dependency_install.sh


Let me explain what's going on there:

 * First we use ``git`` to download ``w4af``'s source code
 * Then we try to run the ``w4af_console`` command, which will most likely fail
   because of missing dependencies. This command will generate a helper script
   at ``/tmp/w4af_dependency_install.sh`` that when run will install all the
   required dependencies.
 * Dependencies are installed by running ``/tmp/w4af_dependency_install.sh``

The framework dependencies don't change too often, but don't be alarmed if after
updating your installation ``w4af`` requires you to install new dependencies.

Supported platforms
-------------------

The framework should work on all Python supported platforms and has been tested
in various Linux distributions, Mac OSX, FreeBSD and OpenBSD.

.. note::

   The platform used for development is Ubuntu 14.04 and running our continuous integration tests
   is Ubuntu 12.04 LTS.

.. warning::

   While in theory you can install w4af in Microsoft Windows, we don't recommend
   nor support that installation process.

One of the ugly details users can find is that ``w4af`` needs to detect the
Operating System / Linux distribution, and then have support for creating the
``/tmp/w4af_dependency_install.sh`` for that specific combination. In other words,
for Ubuntu we use ``apt-get install`` and for Suse we use ``yum install``.

The list of distributions ``w4af`` knows how to generate the installation script
for `is extensive <https://github.com/andresriancho/w4af/tree/master/w4af/core/controllers/dependency_check/platforms>`_ .
If we don't support your distribution, we'll default to Ubuntu.

Installation in Kali
--------------------

.. warning::

   Currently it is not possible to install w4af on kali as pygtk is not any more in the kali packages, see `here <https://pkg.kali.org/pkg/pygtk>`_. So the following instructions currently won't work. You could try building pygtk from source though. 

The easiest way to install ``w4af`` in Kali is:

.. code-block:: console

    apt-get update
    apt-get install -y w4af

This will install the latest packaged version, which might not be the latest
available from our repositories. If the latest version is needed these steps
are recommended:

.. code-block:: console

    cd ~
    apt-get update
    apt-get install -y python-pip w4af
    pip install --upgrade pip
    git clone https://github.com/andresriancho/w4af.git
    cd w4af
    ./w4af_console
    . /tmp/w4af_dependency_install.sh

This will install the latest ``w4af`` at ``~/w4af/w4af_console`` and leave the
packaged version un-touched.

.. note::

   There are two versions in your OS now:
    * ``cd ~/w4af/ ; ./w4af_console`` will run the latest version
    * ``w4af_console`` will run the one packaged in Kali

Installing using Docker
-----------------------

`Docker <https://www.docker.com/>`_ is awesome, it allows users to run ``w4af``
without installing any of it's dependencies. The only pre-requisite is to
`install docker <http://docs.docker.com/installation/>`_ , which is widely
supported.

Once the docker installation is running these steps will yield a running
``w4af`` console:

.. code-block:: console

    $ git clone https://github.com/andresriancho/w4af.git
    $ cd w4af/extras/docker/scripts/
    $ sudo ./w4af_console_docker
    w4af>>>

For advanced usage of ``w4af``'s docker container please read the documentation
at the `docker registry hub <https://registry.hub.docker.com/u/andresriancho/w4af/>`_

Installation in Mac OSX
-----------------------
In order to start the process, you need XCode and MacPorts installed. 

.. code-block:: console

    sudo xcode-select --install
    sudo port selfupdate
    sudo port upgrade outdated
    sudo port install python27
    sudo port select python python27
    sudo port install py27-pip 
    sudo port install py27-libdnet git-core automake gcc48 py27-setuptools autoconf py27-pcapy
    ./w4af_console
    . /tmp/w4af_dependency_install.sh

Those commands should allow you to run ``./w4af_console`` again without any issues,
in order to run the GUI a new dependency set is required:

.. code-block:: console

    sudo port install py27-pygtk py27-pygtksourceview graphviz
    sudo port install py27-webkitgtk
    ./w4af_gui
    . /tmp/w4af_dependency_install.sh

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

Replace ``futures`` with the library that is missing in your system. If the
``pip freeze | grep futures`` command returns an empty result, you'll need to
install the dependency using the ``/tmp/w4af_dependency_install.sh`` command.
Pay special attention to the output of that command, if installation fails
you won't be able to run ``w4af``.

It is important to notice that ``w4af`` requires specific versions of the
third-party libraries. The specific versions required at ``/tmp/w4af_dependency_install.sh``
need to match the ones you see in the output of ``pip freeze``. If the versions
don't match you can always install a specific version using
``pip install --upgrade futures==2.1.5``.

w4af still says I have missing operating system dependencies, what should I do?
_______________________________________________________________________________

You will recognize this when this message appears: "please install the following
operating system packages".

Most likely you're using a Linux distribution that ``w4af`` doesn't know how to
detect. *This doesn't mean that w4af won't work with your distribution!* It just
means that our helper tool doesn't know how to create the
``/tmp/w4af_dependency_install.sh`` script for you.

What you need to do is:

 * Find a match between the Ubuntu package name given in the list and the one
 for your distribution
 * Install it
 * Run ``./w4af_console`` again. Repeat until fixed

Please `create a ticket <https://github.com/andresriancho/w4af/issues/new>`_
explaining the packages you installed, your distribution, etc. and we'll add
the code necessary for others to be able to install ``w4af`` without going
through any manual steps.


How do I ask for support on installation issues?
________________________________________________

You can `create a ticket <https://github.com/andresriancho/w4af/issues/new>`_
containing the following information:

 * Your linux distribution (usually the contents of ``/etc/lsb-release`` will be enough)
 * The contents of the ``/tmp/w4af_dependency_install.sh`` file
 * The output of ``pip freeze``
 * The output of ``python --version``
