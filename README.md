[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)
![](./static/gaultlet.png)

## ThanosDB

A lightweight, fast and simple database based on [msgpack](<https://msgpack.org/index.html>) module. Born out of pure frustration of being unable to use Redis on windows, it came into existence ([Drawbacks of Redis on Windows](<https://redislabs.com/ebook/appendix-a/a-3-installing-on-windows/a-3-1-drawbacks-of-redis-on-windows/>)). It is an open-source key-value store.

In order to justify it's name it will *try* to - 

1. Reduce the read/write time of your database in half.
2. Reduce the size of your storage into half. (*When compared to JSON*)

#### Get, Set, Snap

```python
>>> from thanosdb import thanosdb
>>> db = thanosdb.load('test.db', False)
>>> db.set('key', 'value')
True
>>> db.get('key')
'value'
>>> db.dump()
True
```

#### Testing

Testing in ThanosDB is done using Python's [unittest](https://docs.python.org/2/library/unittest.html) module.

In order to run test go inside package directory and run the following command

```shell
python -m unittest
```

#### Developers - 

- Shril Kumar ([@shril](https://github.com/shril))
- Abhishek Srivastava ([@abhishekai](https://github.com/abhishekai))
- Janpreet Singh ([@janismdhanbad](https://github.com/janismdhanbad))

