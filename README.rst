.. image:: https://gitlab.com/robertomartinezp/brain-slug/raw/master/assets/images/brainslug.svg :align: center

BrainSlug is a framework for *parasitic computing*. Allowing you to
write programs which code and logic live in a computer but actions or
*side-effects* are performed on another.

Example:

.. code-block:: python

   from brainslug import run, slug, body

   @slug(remote=body.platform == 'linux')
   def get_user_id(remote):
       name = 'root'
       with remote.open('/etc/passwd', 'r') as passwd:
           for line in passwd:
               if line.startswith(name):
                   return line.split(':')[2]

   run(get_user_id)


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
