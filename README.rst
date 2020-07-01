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

------------------------
RST and Markdown support
------------------------

By default `ansible-doc-extractor` will output files in .rst format using the built-in Jinja2 template for rst. Pass the ``--markdown`` flag to output files in markdown.

---------------
Custom template
---------------
`ansible-doc-extractor` supports a custom Jinja2 template file via ``--template``. The following variables
are sent to the template:

+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| Variable name      | Type       | Description                                                                         | Module's documentation key                       |
+====================+============+=====================================================================================+==================================================+
| short_description  | str        | Short description of a module.                                                      | short_description                                |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| description        | str / list | Longer description of a module, type depends on the module's `description` type.    | description                                      |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| requirements       | list       | Requirements needed on the host that executes this module.                          | requirements                                     |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| options            | dict       | All module options, often called parameters or arguments.                           | options                                          |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| notes              | list       | Module's additional notes.                                                          | notes                                            |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| seealso            | list       | Details of any important information that doesn’t fit in one of the above sections. | seealso                                          |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| deprecated         | str        | Marks modules that will be removed in future releases                               | deprecated                                       |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| author             | str / list | Author of the module, type can vary depending on how many authors module has.       | author                                           |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| metadata           | dict       | This section provides information about the module                                  | Refers to ANSIBLE_METADATA block in the module.  |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| examples           | str        | Code examples                                                                       | Refers to EXAMPLES block in the module.          |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+
| returndocs         | dict       | This section documents the information the module returns.                          | Refers to RETURN block in the module.            |
+--------------------+------------+-------------------------------------------------------------------------------------+--------------------------------------------------+

The output files will use the same file extension as the custom template file.


You can always refer to the `default Jinja2 template for rst`_ and the `default Jinja2 template for markdown`_.


.. _PyPI: https://pypi.org/
.. _`default Jinja2 template for rst`: https://github.com/xlab-si/ansible-doc-extractor/blob/master/src/ansible_doc_extractor/templates/module.rst.j2
.. _`default Jinja2 template for markdown`: https://github.com/xlab-si/ansible-doc-extractor/blob/master/src/ansible_doc_extractor/templates/module.md.j2


Development setup
-----------------

Getting development environment up and running is relatively simple if we
have ``pipenv`` installed::

   $ pipenv update

To test the extractor, we can run::

   $ pipenv run ansible-doc-extractor
