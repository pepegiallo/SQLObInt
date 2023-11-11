# Add parent directory to system path
import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

# Imports
import psycopg2
from datetime import date, datetime
from interface import UserInterface, setup_db
import random
from control import User
import configparser


def get_connection_pool():
    config = configparser.ConfigParser()
    config.read(r'examples/config.cfg')
    return psycopg2.pool.SimpleConnectionPool(1, 20,
                                              host=config.get('Database', 'host'),
                                              user=config.get('Database', 'user'),
                                              password=config.get('Database', 'password'),
                                              database=config.get('Database', 'database'))


def setup_test(interface: UserInterface, seed=1902):
    random.seed(seed)

    # Klassen
    c_object = interface.create_class('object')
    c_person = interface.create_class('person', c_object)
    c_address = interface.create_class('address', c_object)

    # Attribute
    interface.assign_attribute(interface.create_attribute('created', 'TIMESTAMPTZ', True), c_object, False, 'CURRENT_TIMESTAMP')
    interface.assign_attribute(interface.create_attribute('tag', 'VARCHAR(100)', False), c_object, True)

    interface.assign_attribute(interface.create_attribute('first_name', 'VARCHAR(100)', False), c_person, False)
    interface.assign_attribute(interface.create_attribute('last_name', 'VARCHAR(100)', False), c_person, False)
    interface.assign_attribute(interface.create_attribute('birthday', 'DATE', True), c_person, False, "'01.01.1900'")

    interface.assign_attribute(interface.create_attribute('street', 'VARCHAR(100)', False), c_address, False)
    interface.assign_attribute(interface.create_attribute('house_number', 'VARCHAR(8)', False), c_address, False)
    interface.assign_attribute(interface.create_attribute('postal_code', 'VARCHAR(5)', False), c_address, False)
    interface.assign_attribute(interface.create_attribute('city', 'VARCHAR(100)', False), c_address, False)

    c_object.update_view()
    c_person.update_view()
    c_address.update_view()

    # Assoziationen
    a_person_to_address = interface.create_association('person_to_address', c_person, c_address)
    
    # Testdaten einfügen
    with open('examples/data/sample_first_names.txt', 'r') as file:
        first_names = [name.strip() for name in file.readlines()]
    with open('examples/data/sample_last_names.txt', 'r') as file:
        last_names = [name.strip() for name in file.readlines()]
    all_names = [*first_names, *last_names]

    persons = []
    addresses = []
    n_samples = 100
    for i in range(n_samples):
        o_person = interface.create_object(c_person,
                                          tag=f'Person {i}',
                                          first_name=random.choice(first_names),
                                          last_name=random.choice(last_names),
                                          birthday=date(random.randint(1930, 2005), random.randint(1, 12), random.randint(1, 28)))
        persons.append(o_person)
        o_address = interface.create_object(c_address,
                                            tag=f'Adresse {i}',
                                            street=f"{random.choice(all_names)}{random.choice(['straße', 'weg'])}",
                                            house_number=f"{random.randint(1, 100)}{random.choice(['a', 'b', 'c', 'd', 'e', 'f']) if random.random() < 0.1 else ''}",
                                            postal_code=f"{random.randint(10000, 99999)}",
                                            city=f"{random.choice(all_names)}{random.choice(['stadt', 'dorf', 'ingen', 'heim'])}", )
        addresses.append(o_address)
        interface.bind(o_person, o_address, 'person_to_address')

    # Daten modifizieren
    persons[0].modify(first_name='Fred', last_name='Schlonz')

    # Objekt erhalten
    obj = interface.get_object(persons[0].id, c_person)
    print(obj.dump())
    return obj

def setup_groups(interface: UserInterface, obj):
    root = interface.create_group('public')
    admin = interface.create_group('admin', root)
    admin.assign_user(interface.user)
    admin.assign_object(obj)
    admin.assign_association(interface.get_association_by_name('person_to_address'))


if __name__ == '__main__':
    pool = get_connection_pool()
    root_user = setup_db(pool.getconn())
    interface = UserInterface(root_user, pool)
    print('Database purged')
    
    # Set up test db
    test_obj = setup_test(interface)
    print('Test database built')
    interface.commit()
    interface.disconnect()

    # Benutzergruppen
    setup_groups(interface, test_obj)
    interface.commit()
    print('Benutzergruppen erstellt')
