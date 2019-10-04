Ansible Collection API Documentation Extractor
==============================================

This package contains code for Ansible collection documentation extractor. Its
main audience are Ansible collection maintainers that would like to publish
API docs in the HTML form without having to manually copy the data already
present in the module's metadata.


Quickstart
----------

Documentation extractor is published on PyPI_ and we can install it using
``pip``::

   $ pip install ansible-doc-extractor

If the previous command did not fail, we are ready to start extracting the
documentation::

   $ ansible-doc-extractor \
       /tmp/output-folder \
       ~/.ansible/collections/ansible_collections/my/col/plugins/modules/*.py

This will extract the documentation from modules in ``my.col`` collection and
place resulting rst files into ``/tmp/output-folder``.

.. note::
   Always extract documentation from installed collection. Documentation
   fragment loader fails to combine various parts of the documentation
   otherwise.

.. _PyPI: https://pypi.org/


Development setup
-----------------

Getting development environment up and running is relatively simple if we
have ``pipenv`` installed::

   $ pipenv update

To test the extractor, we can run::

   $ pipenv run ansible-doc-extractor
