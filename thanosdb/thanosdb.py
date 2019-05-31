import msgpack
import os
import signal
import sys

from threading import Thread

def load(location, auto_dump, sig=True):
    '''Return a thanosdb object. location is the path to the msgpack file.'''
    return ThanosDB(location, auto_dump, sig)

class ThanosDB(object):
    """
    Class constructor to create a new ThanosDB instance.

    .. note::

       Install MessagePack (`pip install msgpack`) as ThanosDB internally uses it for storage.
    
    :Example:
 
    >>> from thanosdb import thanosdb
    >>> db = thanosdb.load('avengers.db', True)

        
    :param location: location of msgpack database file
    :type location: string
    :param auto_dump: writes to disk after every operation
    :type auto_dump: boolean
    :param sig: used for graceful shutdown during dump
    :type sig: boolean
    
    """

    key_string_error = TypeError('Only string type is supported as key.')

    def __init__(self, location, auto_dump, sig):
        '''Creates a database object and loads the data from the location path.
        If the file does not exist it will be created on the first update.
        '''
        self.load(location, auto_dump)
        self.dthread = None
        if sig:
            self.set_sigterm_handler()

    def __getitem__(self, item):
        '''Syntax sugar for get()'''
        return self.get(item)

    def __setitem__(self, key, value):
        '''Sytax sugar for set()'''
        return self.set(key, value)

    def __delitem__(self, key):
        '''Sytax sugar for rem()'''
        return self.rem(key)

    def set_sigterm_handler(self):
        '''Assigns sigterm_handler for graceful shutdown during dump()'''
        def sigterm_handler():
            if self.dthread is not None:
                self.dthread.join()
            sys.exit(0)
        signal.signal(signal.SIGTERM, sigterm_handler)

    def load(self, location, auto_dump):
        '''Loads, reloads or changes the path to the db file'''
        location = os.path.expanduser(location)
        self.loco = location
        self.auto_dump = auto_dump
        if os.path.exists(location):
            self._loaddb()
        else:
            self.db = {}
        return True

    def dump(self):
        '''Force dump memory db to file'''
        msgpack.pack(self.db, open(self.loco, 'wb'))
        self.dthread = Thread(
            target=msgpack.pack,
            args=(self.db, open(self.loco, 'wb')))
        self.dthread.start()
        self.dthread.join()
        return True
        
    def _loaddb(self):
        '''Load or reload the msgpack info from the file'''
        self.db = msgpack.unpack(open(self.loco, 'rb'), encoding = 'utf-8')

    def _autodumpdb(self):
        '''Write/save the msgpack dump into the file if auto_dump is enabled'''
        if self.auto_dump:
            self.dump()

    def set(self, key, value):
        '''Set the str value of a key'''
        if isinstance(key, str):
            self.db[key] = value
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def get(self, key):
        '''Get the value of a key'''
        try:
            return self.db[key]
        except KeyError:
            return False

    def getall(self):
        '''Return a list of all keys in db'''
        return self.db.keys()

    def exists(self, key):
        '''Return True if key exists in db, return False if not'''
        return key in self.db

    def rem(self, key):
        '''Delete a key'''
        if not key in self.db: # return False instead of an exception
            return False
        del self.db[key]
        self._autodumpdb()
        return True

    def totalkeys(self, name=None):
        '''Get a total number of keys, lists, and dicts inside the db'''
        if name is None:
            total = len(self.db)
            return total
        else:
            total = len(self.db[name])
            return total

    def append(self, key, more):
        '''Add more to a key's value'''
        tmp = self.db[key]
        self.db[key] = tmp + more
        self._autodumpdb()
        return True

    def lcreate(self, name):
        '''Create a list, name must be str'''
        if isinstance(name, str):
            self.db[name] = []
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def ladd(self, name, value):
        '''Add a value to a list'''
        if self.exists(name):
            self.db[name].append(value)
            self._autodumpdb()
        else:
            self.lcreate(name)
            self.ladd(name, value)
        return True

    def lextend(self, name, seq):
        '''Extend a list with a sequence'''
        self.db[name].extend(seq)
        self._autodumpdb()
        return True

    def lgetall(self, name):
        '''Return all values in a list'''
        return self.db[name]

    def lget(self, name, pos):
        '''Return one value in a list'''
        return self.db[name][pos]

    def lremlist(self, name):
        '''Remove a list and all of its values'''
        number = len(self.db[name])
        del self.db[name]
        self._autodumpdb()
        return number

    def lremvalue(self, name, value):
        '''Remove a value from a certain list'''
        self.db[name].remove(value)
        self._autodumpdb()
        return True

    def lpop(self, name, pos):
        '''Remove one value in a list'''
        value = self.db[name][pos]
        del self.db[name][pos]
        self._autodumpdb()
        return value

    def llen(self, name):
        '''Returns the length of the list'''
        return len(self.db[name])

    def lappend(self, name, pos, more):
        '''Add more to a value in a list'''
        tmp = self.db[name][pos]
        self.db[name][pos] = tmp + more
        self._autodumpdb()
        return True

    def lexists(self, name, value):
        '''Determine if a value exists in a list'''
        return value in self.db[name]

    def dcreate(self, name):
        '''Create a dict, name must be str'''
        if isinstance(name, str):
            self.db[name] = {}
            self._autodumpdb()
            return True
        else:
            raise self.key_string_error

    def dadd(self, name, pair):
        '''Add a key-value pair to a dict, "pair" is a tuple'''
        if self.exists(name):
            self.db[name][pair[0]] = pair[1]
            self._autodumpdb()
        else:
            self.dcreate(name)
            self.dadd(name, pair)
        return True

    def dget(self, name, key):
        '''Return the value for a key in a dict'''
        return self.db[name][key]

    def dgetall(self, name):
        '''Return all key-value pairs from a dict'''
        return self.db[name]

    def drem(self, name):
        '''Remove a dict and all of its pairs'''
        del self.db[name]
        self._autodumpdb()
        return True

    def dpop(self, name, key):
        '''Remove one key-value pair in a dict'''
        value = self.db[name][key]
        del self.db[name][key]
        self._autodumpdb()
        return value

    def dkeys(self, name):
        '''Return all the keys for a dict'''
        return self.db[name].keys()

    def dvals(self, name):
        '''Return all the values for a dict'''
        return self.db[name].values()

    def dexists(self, name, key):
        '''Determine if a key exists or not in a dict'''
        return key in self.db[name]

    def dmerge(self, name1, name2):
        '''Merge two dicts together into name1'''
        first = self.db[name1]
        second = self.db[name2]
        first.update(second)
        self._autodumpdb()
        return True

    def deldb(self):
        '''Delete everything from the database'''
        self.db = {}
        self._autodumpdb()
        return True
