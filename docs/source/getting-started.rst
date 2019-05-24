:tocdepth: 3

Getting Started
===============

Let's cover the basics before going more into detail. We'll start by setting up
a ThanosDB database:

>>> from thanosdb import thanosdb
>>> db = thanosdb.load('example.db', True)

You now have a ThanosDB database that stores its data in ``example.db``.
What about inserting some data? ThanosDB expects the data to be Python ``dict``\s:

>>> db.set('ironman', 'Tony Stark')
>>> db.set('captain-america', 'Steve Rogers')
>>> db.set('thor', 'Thor Odinson')
>>> db.set('black-widow', 'Natasha Romanoff')

Fetching data from database:

>>> print(db.get('ironman'))
Tony Stark
>>> print(db.get('thor'))
Thor Odinson
>>> print(db.getall())
dict_keys(['ironman', 'captain-america', 'thor', 'black-widow'])
>>> '''Returns False if key is not present in db'''
>>> print(db.get('hawkeye'))
False