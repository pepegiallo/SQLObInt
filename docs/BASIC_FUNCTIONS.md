# Basic functions

### Create interface
To create an *UserInterface*, an *User* object and a *ConnectionPool* for the database used are required.
```
from psycopg2 import pool
from interface import UserInterface, setup_db

connection_pool = pool.SimpleConnectionPool(1, 20,
                                            host='hostname.com',
                                            user='postgres',
                                            password='Nice.password123',
                                            database='postgres')

root_user = setup_db(connection_pool.getconn())
interface = UserInterface(root_user, connection_pool)
```