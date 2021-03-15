# rezbefoo
A proof of concept for demoing how Rez's application type plugin can be used.


### Steps

1. Install Plugin

```shell
# in rez venv
cd path-to/rezbefoo
pip install .
# or, for development
pip install -e .
```

2. Configure Rez

```python
# in your rezconfig.py
plugin_module = ["rezbefoo"]
```

3. Run Command

```shell
# on rez activated
rez foo -m
# or,
rez-foo -m
```
