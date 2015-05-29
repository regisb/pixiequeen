Pixie Queen
===========

PixieQueen is a minimal static website generator.

Install
-------

    pip install -e git+https://github.com/regisb/pixiequeen.git#egg=pixiequeen

Usage
-----

The HTML templates are written in the
`Jinja2 <http://jinja.pocoo.org/docs/dev/>`_ template language.
The layout of your website is declared using Python variables in the `pq.py`
file inside the source directory. For an example website, take a look at the
`example/` directory.

Create your first static website::

    pixify ./example ./www

You can start an HTTP server If you wish to view your rendered website at the
same time as you create it::

    pixify --serve ./example ./www
