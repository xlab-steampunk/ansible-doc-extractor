Ansible Collection API Documentation Extractor
==============================================

This package contains code for Ansible collection documentation extractor. Its
main audience are Ansible collection maintainers that would like to publish
API docs in the HTML form without having to manually copy the data already
present in the module's metadata.


Installation
------------

Currently, no version has been published yet on PyPI. But installing from
source is also relatively simple if you have ``pipenv`` installed::

   $ export export SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0
   $ pipenv update

Now we can extract the documentation from our modules by running::

   $ pipenv run ansible-doc-extract \
       ~/path/to/output/folder \
       ~/path/to/first/module.py \
       ~/path/to/second/module.py


.. note::
   Fragment loaded might have some troubles with collections that are not
   installed yet.
