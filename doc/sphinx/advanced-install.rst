Advanced installation
=====================

.. warning::

   None of these installation methods are recommended for new users.
   Please refer to :doc:`install` for the most common ways to get started with ``w4af``.

Bleeding edge vs. stable
------------------------

We develop ``w4af`` using ``git flow``, this means that we'll always have at least
two branches in our repository:

 * ``main``: The branch where our latest stable code lives. We take it very
 seriously to make sure all unit tests ``PASS`` in this branch.
 * ``develop``: The branch where new features are merged and tested. Not as
 stable as ``main`` but we try to keep this one working too.

Advanced users might want to be on the bleeding edge aka ``develop`` to get the
latest features, while users using ``w4af`` for continuous scanning and other
tasks which require stability would choose ``main`` (our stable release).

Moving to bleeding edge ``w4af`` is easy:

.. code-block:: bash

    git clone https://github.com/w4af/w4af.git
    cd w4af/
    git checkout develop
    python -m pip install --upgrade pipenv wheel
    pipenv install
    npm install
    pipenv shell
    ./w4af_console

To the regular installation procedure we added the ``git checkout develop``,
that's it! If you're running in this branch and find an issue, please report
it back to us too. We're interested in hearing about **any issues** users identify.

