.. thanosdb documentation master file, created by
   sphinx-quickstart on Fri May 24 16:14:25 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ThanosDB!
====================

Welcome to ThanosDb, a lightweight, fast and compact database based on msgpack module.
This project is inspired by redis. It is licensed with the MIT License.
Github_.

>>> from thanosdb import thanosdb
>>> db = thanosdb.load('test.db', False)
>>> db.set('key', 'value')
True
>>> db.get('key')
'value'
>>> db.dump()
True

User's Guide
------------

.. toctree::
   :maxdepth: 2
   
   installation
   getting-started

API Reference
-------------

.. toctree::
   :maxdepth: 2

   api

.. References
.. _GitHub: http://github.com/shril/thanosdb/