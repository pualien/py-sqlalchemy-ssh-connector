![sqlalchemy-connector](https://github.com/pualien/py-sqlalchemy-ssh-connector/blob/master/images/logo.png?raw=true)

# py-sqlalchemy-ssh-connector
[![PyPI Latest Release](https://img.shields.io/pypi/v/sqlalchemy-connector.svg)](https://pypi.org/project/sqlalchemy-connector/)
[![PyPI Build](https://github.com/pualien/py-sqlalchemy-ssh-connector/workflows/PyPI%20Build/badge.svg)](https://github.com/pualien/py-sqlalchemy-ssh-connector/actions)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/sqlalchemy-connector)](https://pypi.org/project/sqlalchemy-connector/))
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqlalchemy-connector.svg)](https://pypi.org/project/sqlalchemy-connector/))

Python library to connect to SQLAlchemy with SSH Tunnel.

## Where to get it

The source code is currently hosted on GitHub at:
<https://github.com/pualien/py-sqlalchemy-ssh-connector>

Binary installers for the latest released version are available at the
[Python package index](https://pypi.org/project/sqlalchemy-connector/)

```sh
pip install sqlalchemy-connector
```

### Example 1


```python
from alchemy_connector import SQLAlchemySession

session = SQLAlchemySession('db.example.com')
result = session.execute('''select * from ecommerce_transactions limit 1''')
session.stop()
# session.start()
```

### Example 2
{adapter}://{username}:{password}@{host}:{port}/{database}
```python
session = SQLAlchemySession(
    host='db.example.com',
    uri='mysql+pymysql://user:password@127.0.0.1:3306/db'
)
...
session.stop()
```

### Example 3

```python
session = SQLAlchemySession(
    host='db.example.com',
    user='myuser',
    password='mypassword',
)
...
session.stop()
```

### Example 4

```python
session = SQLAlchemySession(
    host='db.example.com',
    port='21',
    user='myuser',
    key='/home/myplace/.ssh/id_rsa2',
    to_port='37017',
    to_host='0.0.0.0'
)
...
session.stop()
```
