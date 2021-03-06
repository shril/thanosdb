import os
import signal
import sys

from threading import Thread

import msgpack

def load(location, auto_dump, sig=True):
    '''Return a thanosdb object. location is the path to the msgpack file.'''
    return ThanosDB(location, auto_dump, sig)

class ThanosDB(object):
    '''
    A key-value based data structure which internally uses msgpack
    for storing data. Serialization and deserialization of data
    happens during dumping and loading operations.

    .. note::

       Install MessagePack as ThanosDB internally uses it for storage.

    :Example:

    >>> from thanosdb import thanosdb
    >>> db = thanosdb.load('avengers.db', True)

    :param location: location of msgpack database file
    :type location: string
    :param auto_dump: writes to disk after every operation if True
    :type auto_dump: boolean
    :param sig: used for graceful shutdown during dump if True
    :type sig: boolean
    '''

    key_string_error = TypeError('Only string type is supported as key.')

    def __init__(self, location, auto_dump, sig):
        '''Creates a database object and loads the data from the location path.
        If the file does not exist it will be created on the first update.
        '''
        self.load(location, auto_dump)
        self.dthread = None
        if sig:
            self._set_sigterm_handler()

    def __getitem__(self, item):
        '''Syntax sugar for get()'''
        return self.get(item)

    def __setitem__(self, key, value):
        '''Sytax sugar for set()'''
        return self.set(key, value)

    def __delitem__(self, key):
        '''Sytax sugar for rem()'''
        return self.rem(key)

    def _set_sigterm_handler(self):
        '''Assigns sigterm_handler for graceful shutdown during dump()

        *Ensures that the key-value operations get written to disk in case of db failure\
            to maintain consistency.*
        '''
        def sigterm_handler():
            if self.dthread is not None:
                self.dthread.join()
            sys.exit(0)
        signal.signal(signal.SIGTERM, sigterm_handler)

    def load(self, location, auto_dump):
        '''Loads, reloads or changes the path to the db file

        :Example:

        >>> from thanosdb import thanosdb
        >>> db = thanosdb.load('avengers.db', True, False)

        :param location: location of msgpack database file
        :type location: string
        :param auto_dump: writes to disk after every operation
        :type auto_dump: boolean
        :param sig: used for graceful shutdown during dump
        :type sig: boolean
        '''
        location = os.path.expanduser(location)
        self.loco = location
        self.auto_dump = auto_dump
        if os.path.exists(location):
            self._loaddb()
        else:
            self.db = {}
        return True

    def dump(self):
        '''
        Force dump memory db to file.

        :Example:

        >>> db.dump()
        True

        :return: True
        :rtype: Boolean
        '''
        msgpack.pack(self.db, open(self.loco, 'wb'))
        self.dthread = Thread(
            target=msgpack.pack,
            args=(self.db, open(self.loco, 'wb')))
        self.dthread.start()
        self.dthread.join()
        return True

    def _loaddb(self):
        '''Load or reload the msgpack info from the file'''
        self.db = msgpack.unpack(open(self.loco, 'rb'), encoding='utf-8')

    def _autodumpdb(self):
        '''Write/save the msgpack dump into the file if auto_dump is enabled'''
        if self.auto_dump:
            self.dump()

    def set(self, key, value):
        '''Set the str value of a key

        :Example:

        >>> db.set('ironman', 'Tony Stark')
        True

        :param key: Name of the key to add in db
        :type key: string
        :param value: Value associated with the key
        :type value: string, dict, list
        :return: True for successful execution else false.
        :rtype: boolean
        '''
        if isinstance(key, str):
            self.db[key] = value
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def get(self, key):
        '''Get the value of a key

        :Example:

        >>> db.get('ironman')
        'Tony Stark'

        :param key: Name of key in db
        :type key: string
        :return: Value if key present else returns false.
        '''
        try:
            return self.db[key]
        except KeyError:
            return False

    def getall(self):
        '''Return a list of all keys in db

        :Example:

        >>> db.getall()
        dict_keys(['ironman', 'thor', 'black-widow'])

        :return: List of all keys in db.
        :rtype: dict_keys
        '''
        return self.db.keys()

    def exists(self, key):
        '''Return True if key exists in db, return False if not

        :Example:

        >>> db.exists('ironman')
        True

        :param key: input key
        :type key: string
        :return: True if key exists in db, else False.
        :rtype: Boolean
        '''
        return key in self.db

    def rem(self, key):
        '''Delete a key

        :Example:

        >>> db.rem('ironman')
        True

        :param key: Name of the key to add in db
        :type key: string
        :return: True if key exists in db and gets deleted, else False if no such key in db.
        :rtype: Boolean
        '''
        if not key in self.db: # return False instead of an exception
            return False
        del self.db[key]
        self._autodumpdb()
        return True

    def totalkeys(self, name=None):
        '''Get a total number of keys, lists, and dicts inside the db
        
        :Example:

        >>> db.totalkeys()
        5

        :param name: None or name of key of dict
        :type name: string
        :return: Count of number of keys of dict.
        :rtype: int
        '''
        if name is None:
            total = len(self.db)
            return total
        else:
            total = len(self.db[name])
            return total

    def append(self, key, more):
        '''Add more to a key's value
        
        :Example:

        >>> db.set('thor', 'Thor Odinson')
        True
        >>> db.append('thor', ' - God of Thunder')
        True
        >>> db.get('thor')
        'Thor Odinson - God of Thunder'

        :param key: Name of key in db
        :type key: string
        :param more: Value associated with key
        :type more: string
        :return: True if successful execution else false.
        :rtype: Boolean
        
        '''
        tmp = self.db[key]
        self.db[key] = tmp + more
        self._autodumpdb()
        return True

    def lcreate(self, name):
        '''Create an empty list with key name, name must be str
        
        :Example:

        >>> db.lcreate('avengers')

        :param name: key of dict
        :type name: string
        :return: True if successful execution else false.
        :rtype: Boolean
        '''
        if isinstance(name, str):
            self.db[name] = []
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def ladd(self, name, value):
        '''Add a value to a list
        
        :Example:

        >>> db.ladd('avengers', 'Iron Man')

        :param name: key of dict
        :type name: string
        :param value: value to be appended to list with key *name*
        :type value: string
        :return: True if successful execution else false.
        :rtype: Boolean
        
        '''
        if self.exists(name):
            self.db[name].append(value)
            self._autodumpdb()
        else:
            self.lcreate(name)
            self.ladd(name, value)
        return True

    def lextend(self, name, seq):
        '''Extend a list with a sequence
        
        :Example:

        >>> db.lextend('avengers', ['Thor', 'Hawkeye'])
        True

        :param name: Name of the key of list in db
        :type name: string
        :param seq: list to be appended to list associated with key *name* in db
        :type value: list
        :return: True if successful execution else false.
        :rtype: Boolean
        '''
        self.db[name].extend(seq)
        self._autodumpdb()
        return True

    def lgetall(self, name):
        '''Return all values in a list
        
        :Example:

        >>> db.lgetall('avengers')
        ['ironman', 'thor', 'captain-america', 'hulk']

        :param name: Name of the key of list in db
        :type name: string
        :return: List associated with key *name* in db else false if key not present.
        :rtype: list

        '''
        return self.db[name]

    def lget(self, name, pos):
        '''Return one value in a list
        
        :Example:

        >>> db.lget('avengers', 1)
        'ironman'

        :param name: Name of the key of list in db
        :type name: string
        :param pos: position of element in list
        :type pos: int
        :return: Value at index *pos* of list associated with key *name* in db.
        '''
        return self.db[name][pos]

    def lremlist(self, name):
        '''Remove a list and all of its values
        
        :Example:

        >>> db.lremlist('avengers')

        :param name: Name of the key of list in db
        :type name: string
        :return: Length of list deleted from db with key *name*.
        :rtype: int
        
        '''
        number = len(self.db[name])
        del self.db[name]
        self._autodumpdb()
        return number

    def lremvalue(self, name, value):
        '''Remove a value from a certain list
        
        :Example:

        >>> db.lremvalue('avengers', 'Black Widow')
        True

        :param name: Name of the key of list in db
        :type name: string
        :param value: Value to be deleted from list
        :type value: string
        :return: True if successful execution else false.
        :rtype: Boolean
        
        '''
        self.db[name].remove(value)
        self._autodumpdb()
        return True

    def lpop(self, name, pos):
        '''Remove one value in a list
        
        :Example:

        >>> db.lpop('avengers', 1)

        :param name: Name of the key of list in db
        :type name: string
        :param pos: index of the item in the list to be deleted
        :type pos: int
        :return: Value of deleted item.
        :rtype: string
        '''
        value = self.db[name][pos]
        del self.db[name][pos]
        self._autodumpdb()
        return value

    def llen(self, name):
        '''Returns the length of the list
        
        :Example:

        >>> db.llen('avengers')
        4

        :param name: Name of the key of list in db
        :type name: string
        :return: Length of list associated with key *name* in dict.
        :rtype: int
        '''
        return len(self.db[name])

    def lappend(self, name, pos, more):
        '''Add more to a value in a list
        
        :Example:

        >>> db.lappend('ironman', 2, 'Jarvis')

        :param name: Name of key of list
        :type name: string
        :param pos: Index of list
        :type pos: int
        :param more: string to be added with element at index *pos* of list associated with key *name*
        :type more: string
        :return: True if successful execution else false.
        :rtype: Boolean
        
        '''
        tmp = self.db[name][pos]
        self.db[name][pos] = tmp + more
        self._autodumpdb()
        return True

    def lexists(self, name, value):
        '''Determine if a value exists in a list
        
        :Example:

        >>> db.lexists('avengers', 'ironman')
        False

        :param name: Name of key of list in db
        :type name: string
        :param value: Element to check if present in list with key *name*
        :type value: string
        :return: True if *value* exists in list else false.
        :rtype: Boolean
        '''
        return value in self.db[name]

    def dcreate(self, name):
        '''
        Create a dict, name must be str

        :Example:

        >>> db.dcreate('infinity-stones')
        True

        :param name: Name of the key of dict in db
        :type name: string
        :return: True if *name* is string else Key-String Error.
        :rtype: Boolean
        '''
        if isinstance(name, str):
            self.db[name] = {}
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def dadd(self, name, pair):
        '''
        Add a key-value pair to a dict, "pair" is a tuple

        :Example:
        
        >>> db.dadd('infinity-stone', ('Soul Stone', 'Vormir'))
        True
        >>> db.dadd('infinity-stone', ('Time Stone', 'Earth'))
        True
        >>> db.get('infinity-stone')
        {'Soul Stone': 'Vormir', 'Time Stone': 'Earth'}

        :param name: Name of the key of dict in db
        :type name: string
        :param pair: key-value tuple to be added
        :type pair: tuple
        :return: True if *name* is string else Key-String Error.
        :rtype: Boolean
        '''
        # import pdb; pdb.set_trace()
        if self.exists(name):
            self.db[name][pair[0]] = pair[1]
            self._autodumpdb()
        else:
            self.dcreate(name)
            self.dadd(name, pair)
        return True

    def dget(self, name, key):
        '''
        Return the value for a key in a dict

        :Example:

        >>> db.dget('infinity-stone', 'Soul Stone')
        'Vormir'

        :param name: Name of the key of dict in db
        :type name: string
        :param key: Name of key in dict
        :type key: string
        :return: Value if key is found in the dict
        '''
        return self.db[name][key]

    def dgetall(self, name):
        '''
        Return all key-value pairs from a dict

        :Example:

        >>> db.dgetall('infinity-stone')
        {'Soul Stone': 'Vormir', 'Time Stone': 'Earth'}

        :param name: Name of the key of dict in db
        :type name: string
        :return: data stored in dict
        :rtype: dict
        '''
        return self.db[name]

    def drem(self, name):
        '''
        Remove a dict and all of its pairs

        :Example:

        >>> db.drem('infinity-stone')
        True

        :param name: Name of the key of dict in db
        :type name: string
        :return: True
        :rtype: Boolean
        '''
        del self.db[name]
        self._autodumpdb()
        return True

    def dpop(self, name, key):
        '''
        Remove one key-value pair in a dict

        :Example:

        >>> db.dpop('infinity-stone', 'Soul Stone')
        'Vormir'

        :param name: Name of the key in db
        :type name: string
        :param key: Name of the key in dict
        :type key: string
        :return: Value stored in key
        :rtype: datatype of value
        '''
        value = self.db[name][key]
        del self.db[name][key]
        self._autodumpdb()
        return value

    def dkeys(self, name):
        '''
        Return all the keys for a dict

        :Example:

        >>> db.dkeys('infinity-stone')
        dict_keys(['Soul Stone', 'Time Stone'])

        :param name: Name of key of dict in db
        :type name: string
        :return: dict_keys
        :rtype: dict_keys
        '''
        return self.db[name].keys()

    def dvals(self, name):
        '''
        Return all the values for a dict

        :Example:

        >>> db.dvals('infinity-stone')
        dict_values(['Soul Stone', 'Time Stone'])

        :param name: Name of key of dict
        :type name: string
        :return: dict_values
        :rtype: dict_values
        '''
        return self.db[name].values()

    def dexists(self, name, key):
        '''
        Determine if a key exists or not in a dict

        :Example:

        >>> db.dexists('infinity-stone', 'Soul Stone')
        True

        :param name: Name of key of dict in db
        :type name: string
        :param key: key in the dict
        :type key: string
        :return: True if key is found in the dict
        :rtype: Boolean
        '''
        return key in self.db[name]

    def dmerge(self, name1, name2):
        '''
        Merge two dicts together into name1

        :Example:

        >>> db.dadd('stone-owners', ('Dr. Strange', 'Time Stone'))
        >>> db.dmerge('infinity-stone', 'stone-owners')
        True

        :param name1: Name of key of first dict
        :type name1: string
        :param name2: Name of key of second dict
        :type name2: string
        :return: True
        :rtype: Boolean
        '''
        first = self.db[name1]
        second = self.db[name2]
        first.update(second)
        self._autodumpdb()
        return True

    def deldb(self):
        '''
        Delete everything from the database

        :Example:

        >>> db.deldb()
        True

        '''
        self.db = {}
        self._autodumpdb()
        return True
