# Basic functions

### Create interface
To create an *UserInterface*, an *User* object and a *ConnectionPool* for the database used are required.
```
from psycopg2 import pool

def get_connection_pool():
    return pool.SimpleConnectionPool(1, 20,
                                     host=os.environ.get('POI_DB_HOST'),
                                     user=os.environ.get('POI_DB_USER'),
                                     password=os.environ.get('POI_DB_PASSWORD'),
                                     database=os.environ.get('POI_DB_DATABASE'))

user = User('2ac51f42-548c-4faf-b1e4-85a3b77acf2c')
interface = UserInterface(user, get_connection_pool())
```