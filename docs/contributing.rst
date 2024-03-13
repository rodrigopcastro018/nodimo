.. _contributing:

============
Contributing
============

This section provides some instructions for those who want to contribute with
the development of Nodimo.

Development Environment
-----------------------

Git and GitHub
^^^^^^^^^^^^^^
Nodimo is available on `GitHub`_ and uses `Git`_ for source control.

To get the source code from GitHub run::

    git clone https://github.com/rodrigopcastro018/nodimo

Virtual Environment
^^^^^^^^^^^^^^^^^^^

Isolate you development environment by using virtual environments. In the repository
folder, execute::

    python -m venv venv

Activate the virtual environment by running::

    venv/scripts/activate

From the repository folder, install Nodimo in editable mode with::

    pip install -e .

Testing
-------

To install Nodimo testing dependencies, run::

    pip install .[test]

Nodimo contains type hints that can be checked with `mypy`_ by running::

    mypy

Main functionalities can be tested with `pytest`_ by executing::

    pytest

The `nbmake`_ plugin is responsible for testing the `ipynb` files in the `tests` folder.

Testing multiple environments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nodimo can be tested for multiple versions of its dependencies and python.

Multiple python versions can be installed with `pyenv`_ (or `pyenv-win`_ for windows).
After installing ``pyenv``, install the desired versions of python by running::

    pyenv install 3.9.0 3.10.0 3.11.0 3.12.0

And set them to local with::

    pyenv local 3.9.0 3.10.0 3.11.0 3.12.0

The package `tox`_ is used for test automation. It's recommended to follow the
instructions in the website on how to install it. During the development of
Nodimo on windows, it was also necessary the installation of `tox-pyenv-redux`_
to enable the discovery of the ``pyenv`` python environments by ``tox``.

With ``tox`` configurations already contained in the setup file `pyproject.toml`, 
all that remains is to run, in the repository folder::

    tox

And ``tox`` will run tests and type checking on the configured environments.

Documentation
-------------

The documentation is built with `Sphinx`_, using `Furo`_ as a theme. Tutorials 
made with `jupyter notebook`_ were added to the documentation using the extension
`nbsphinx`_, and docstrings follow the `numpydoc`_ standard.

To install all these dependencies, just execute::

    pip install .[doc]

From the `docs` folder, create the `html` files by running:

* on windows::

    ./make.bat html

* on linux or mac::

    make html

.. _GitHub: https://github.com/rodrigopcastro018/nodimo
.. _Git: https://git-scm.com/
.. _mypy: https://mypy-lang.org/
.. _pytest: https://docs.pytest.org/
.. _nbmake: https://github.com/treebeardtech/nbmake
.. _pyenv: https://github.com/pyenv/pyenv
.. _pyenv-win: https://github.com/pyenv-win/pyenv-win
.. _tox: https://tox.wiki/
.. _tox-pyenv-redux: https://github.com/un-def/tox-pyenv-redux
.. _Sphinx: https://www.sphinx-doc.org/
.. _Furo: https://github.com/pradyunsg/furo
.. _jupyter notebook: https://github.com/jupyter/notebook
.. _nbsphinx: https://nbsphinx.readthedocs.io/
.. _numpydoc: https://numpydoc.readthedocs.io/