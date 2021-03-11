# rezbefoo
A proof of concept for demoing how Rez's application type plugin can be used.


### Option A

```console
$ # in rez venv
$ cd path-to/rezbefoo
$ pip install -e .
```

```console
$ # in rez venv
$ cd path-to/rezbefoo
$ pip install .
```

```python
# in your rezconfig.py
plugin_module = ["rezbefoo"]
```

```console
$ # on rez activated
$ rez foo -m
$ # or,
$ rez-foo -m
```

### Option B

```python
# in your rezconfig.py
plugin_path = ["path-to/rezbefoo/src/rezbefoo"]
```

```console
$ # on rez activated
$ rez foo -m
```
