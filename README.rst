.. warning::

   BrainSlug is a work in progress. Code may change rapidly in incompatible manners. Any question, please drop us an issue
   
.. image:: https://raw.githubusercontent.com/BBVA/brainslug/master/assets/images/brainslug.png
   :align: center



.. image:: https://img.shields.io/pypi/v/brainslug.svg
   :target: https://pypi.org/project/brainslug/

.. image:: https://img.shields.io/circleci/project/github/BBVA/brainslug/master.svg
   :target: https://circleci.com/gh/BBVA/brainslug/tree/master

.. image:: https://readthedocs.org/projects/brainslug/badge/?version=latest
   :target: https://brainslug.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/github/license/BBVA/brainslug.svg

BrainSlug is a framework for *parasitic computing*. Allowing you to
write programs which code and logic live in a computer but actions or
*side-effects* are performed on another.

Example:

.. code-block:: python

   from brainslug import run, slug, body

   @slug(remote=body.platform == 'linux')
   def get_root_shell(remote):
       with remote.open('/etc/passwd', 'r') as passwd:
           for line in passwd:
               if line.startswith('root'):
                   return line.split(':')[-1]

   run(get_root_shell)


This code should be run in a computer we call *slug*. Running this code
will open the port 8080 and stop execution until a *body* connects to
it.

To connect a *body*, in a remote system run the following:

.. code-block:: bash

   $ curl http://<slug-ip>:8080/boot/python | python

This will spawn the *body* to life and connect it with the *slug*.

The program continues running in the *slug*, but the file reads are
performed in the *body*.

More examples on the example section.
