import psycopg2
import psycopg2.extras
from psycopg2 import pool
from control import Class, Attribute, Association, AttributeAssignment, Object, User, Group
from cache import StructureCache

def setup_db(connection, filename_init_script: str = 'setup/init.sql'):
        """ Leeren und initialisiert die Datenbank, gibt Root-Benutzer zurück """
        cursor = connection.cursor()
        cursor.execute("""
        DROP SCHEMA IF EXISTS permission CASCADE; 
        DROP SCHEMA IF EXISTS data CASCADE;
        DROP SCHEMA IF EXISTS association CASCADE;
        DROP SCHEMA IF EXISTS structure CASCADE;
        """)
        with open(filename_init_script, 'r') as file:
            cursor.execute(file.read())
        root_user_id = cursor.fetchone()[0]
        connection.commit()
        return User(root_user_id)

class UserInterface:
    def __init__(self, user: User, connection_pool: pool.SimpleConnectionPool):
        self.user = user
        self.connection_pool = connection_pool
        self.structure_cache = StructureCache()
        self.current_connection = None

    def connect(self):
        """ Weist der aktuelle Datenbankverbindung eine neue Datenbankverbindung aus dem Connection Pool zu """
        self.current_connection = self.connection_pool.getconn()

    def commit(self):
        """ Führt einen Commit mit der aktuellen Datenbankverbindung durch """
        self.current_connection.commit()

    def disconnect(self):
        """ Trennt die aktuelle Datenbankverbindung """
        if self.current_connection:
            self.current_connection.close()
            self.current_connection = None

    def get_connection(self):
        """ Gibt eine neue Datenbankverbindung aus dem Connection Pool zurück """
        if not self.current_connection:
            self.connect()
        return self.current_connection

    ################################################## Klasse ##################################################
    def create_class(self, name: str, parent: Class = None) -> Class:
        """ Erstellt eine neue Objektklasse und gibt Klassenobjekt zurück """
        cursor = self.get_connection().cursor()
        if parent:
            cursor.execute('INSERT INTO structure.class (name, parent_id) VALUES (%s, %s) RETURNING id', (name, parent.id))
        else:
            cursor.execute('INSERT INTO structure.class (name) VALUES (%s) RETURNING id', (name,))
        id = cursor.fetchone()[0]
        cursor.execute(f"CREATE TABLE data.{name} (id UUID {f'REFERENCES data.{parent.name}(id)' if parent else 'REFERENCES data.meta(id)'} PRIMARY KEY)")
        return Class(self, id, name, None if parent is None else parent.id)

    def get_class_from_db_by_id(self, id: str) -> Class:
        """ Gibt Klassenobjekt per Datenbankzugriff anhand dessen ID zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT name, parent_id FROM class WHERE id = %s', (id,))
        res = cursor.fetchone()
        if res:
            return Class(id, res[0], res[1])
        else:
            return None

    def get_class_by_id(self, id: str) -> Class:
        """ Gibt Klassenobjekt anhand dessen ID zurück """
        class_ = self.structure_cache.get_class('id', id)
        if not class_:
            class_ = self.get_class_from_db_by_id(id)
        return class_

    def get_class_from_db_by_name(self, name: str) -> Class:
        """ Gibt Klassenobjekt per Datenbankzugriff anhand dessen Name zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, parent_id FROM structure.class WHERE name = %s', (name,))
        res = cursor.fetchone()
        if res:
            return Class(res[0], name, res[1])
        else:
            return None

    def get_class_by_name(self, name: str) -> Class:
        """ Gibt Klassenobjekt anhand dessen Namen zurück """
        class_ = self.structure_cache.get_class('name', name)
        if not class_:
            class_ = self.get_class_from_db_by_name(name)
        return class_

    def get_assigned_attributes_from_db(self, class_: Class):
        """ Gibt per Datenbankzugriff die der übergebenen Klasse zugewiesen Attribute zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT a.id FROM structure.attribute_assignment as aa JOIN structure.attribute as a ON aa.attribute_id = a.id WHERE aa.class_id = %s', (class_.id,))
        return [self.get_attribute_by_id(row[0]) for row in cursor.fetchall()]

    def get_assigned_attributes(self, class_: Class):
        """ Gibt die der übergebenen Klasse zugewiesen Attribute zurück """
        return class_.get_assigned_attributes()

    def update_class_view(self, class_: Class):
        """ Erstellt oder aktualisiert in der Datenbank eine View zum Anzeigen aller Objekte der übergebenen Klasse """

        # Query erzeugen
        class_attributes = {}
        for current_class in class_.get_family_tree():
            class_attributes[current_class.name] = [a.name for a in current_class.get_assigned_attributes()]
        cols = []
        joins = []
        str_origin_class = None
        for c in class_attributes:
            cols.append(', '.join([f'data.{c}.{a}' for a in class_attributes[c]]))
            if not str_origin_class:
                str_origin_class = c
            else:
                joins.append(f'JOIN data.{c} ON data.{str_origin_class}.id = data.{c}.id')

        # Datenbankabfrage
        cursor = self.get_connection().cursor()
        cursor.execute(f"CREATE OR REPLACE VIEW {class_.get_view_name()} AS SELECT {', '.join([f'data.{str_origin_class}.id', *cols])} FROM data.{str_origin_class} {', '.join(joins)}")

    ################################################## Attribut ##################################################
    def create_attribute(self, name: str, generator: str, indexed: bool) -> Attribute:
        """ Erstellt ein neues Attribut und gibt Attributobjekt zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO structure.attribute (name, generator, indexed) VALUES (%s, %s, %s) RETURNING id', (name, generator, indexed))
        return Attribute(self, cursor.fetchone()[0], name, generator, indexed)

    def get_attribute_from_db_by_id(self, id: str) -> Attribute:
        """ Gibt Attributobjekt per Datenbankzugriff anhand dessen ID zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT name, generator, indexed FROM structure.attribute WHERE id = %s', (id,))
        res = cursor.fetchone()
        if res:
            return Attribute(self, id, res[0], res[1], res[2])
        else:
            return None

    def get_attribute_by_id(self, id: str) -> Attribute:
        """ Gibt Attributobjekt anhand dessen ID zurück """
        attribute = self.structure_cache.get_attribute('id', id)
        if not attribute:
            attribute = self.get_attribute_from_db_by_id(id)
        return attribute

    def get_attribute_from_db_by_name(self, name: str) -> Attribute:
        """ Gibt Attributobjekt per Datenbankzugriff anhand dessen Name zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, generator, indexed FROM structure.attribute WHERE name = %s', (name,))
        res = cursor.fetchone()
        if res:
            return Attribute(self, res[0], name, res[1], res[2])
        else:
            return None

    def get_attribute_by_name(self, name: str) -> Attribute:
        """ Gibt Attributobjekt anhand dessen Namen zurück """
        attribute = self.structure_cache.get_attribute('name', name)
        if not attribute:
            attribute = self.get_attribute_from_db_by_name(name)
        return attribute

    def assign_attribute(self, attribute: Attribute, class_: Class, nullable: bool, default: str = None) -> bool:
        """ Weist ein Attribut einer Klasse zu """
        cursor = self.get_connection().cursor()
        generator = f"{attribute.generator}{' NOT NULL' if not nullable else ''}{f' DEFAULT {default}' if default else ''}"
        cursor.execute(f"""
        INSERT INTO structure.attribute_assignment (class_id, attribute_id, nullable, "default") VALUES (%s, %s, %s, %s);
        ALTER TABLE data.{class_.name} ADD COLUMN {attribute.name} {generator};
        {f'CREATE INDEX {class_.name}_{attribute.name} ON data.{class_.name}({attribute.name});' if attribute.indexed else ''}
        """, (class_.id, attribute.id, nullable, default))
        return AttributeAssignment(self, class_.id, attribute.id, nullable, default)

    ################################################## Assoziation ##################################################
    def create_association(self, name: str, origin_class: Class, target_class: Class) -> Association:
        """ Erstellt eine neue Assoziation und gibt Assoziationsobjekt zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO structure.association (name, origin_class_id, target_class_id) VALUES (%s, %s, %s) RETURNING id', (name, origin_class.id, target_class.id))
        id = cursor.fetchone()[0]
        cursor.execute(f"""
        CREATE TABLE association.{name} (
            origin_id UUID REFERENCES data.{origin_class.name},
            target_id UUID REFERENCES data.{target_class.name},
            PRIMARY KEY (origin_id, target_id)
        )
        """)
        return Association(self, id, name, origin_class.id, target_class.id)

    def get_association_from_db_by_name(self, name: str) -> Association:
        """ Gibt Assoziationsobjekt per Datenbankzugriff anhand dessen Name zurück """
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, origin_class_id, target_class_id FROM structure.association WHERE name = %s', (name,))
        res = cursor.fetchone()
        if res:
            return Association(self, res[0], name, res[1], res[2])
        else:
            return None

    def get_association_by_name(self, name: str) -> Association:
        """ Gibt Assoziationsobjekt anhand dessen Namen zurück """
        association = self.structure_cache.get_association('name', name)
        if not association:
            association = self.get_association_from_db_by_name(name)
        return association

    ################################################## Objekt ##################################################
    def create_object(self, class_: Class, **attributes) -> Object:
        """ Erstellt ein Objekt der angegebenen Klasse mithilfe der angegebenen Attribute (att1=x, att2=y, ...) """
        cursor = self.get_connection().cursor()

        # Metadaten des Objeks einfügen
        cursor.execute('INSERT INTO data.meta (class_id, creator_id) VALUES (%s, %s) RETURNING id', (class_.id, self.user.id))
        id = cursor.fetchone()[0]

        query = []
        values = []
        for current_class in class_.get_family_tree():

            # Einzufügende Attribute ermitteln
            class_attributes = [a.name for a in current_class.get_assigned_attributes()]
            insert_attributes = [a for a in attributes if a in class_attributes]

            # Query zusammenbauen
            str_cols = ', '.join(insert_attributes)
            str_values = ', '.join(['%s'] * len(insert_attributes))
            values.append(id)
            values.extend([attributes[key] for key in insert_attributes])
            query.append(f'INSERT INTO data.{current_class.name} (id, {str_cols}) VALUES (%s, {str_values});')

        # Query ausführen
        if len(query) > 0:
            cursor.execute('\n'.join(query), tuple(values))

        return Object(self, id, class_, **attributes)

    def get_object(self, id: str, class_: Class) -> Object:
        """ Gibt ein Objekt anhand der übergebenen ID und Klasse zurück """
        cursor = self.get_connection().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(f'SELECT * FROM {class_.get_view_name()} WHERE id = %s', (id,))
        row = cursor.fetchone()
        return Object(self, id, class_, **{a: v for a, v in row.items() if a != 'id'})

    def modify(self, object_, **attributes):
        """ Aktualisiert die übergebenen Attribute des übergebenen Objekts """
        query = []
        values = []
        for current_class in object_.get_class().get_family_tree():

            # Einzufügende Attribute ermitteln
            class_attributes = [a.name for a in current_class.get_assigned_attributes()]
            insert_attributes = [a for a in attributes if a in class_attributes]

            # Query erzeugen
            if len(insert_attributes) > 0:
                str_update = ','.join([f'{a} = %s' for a in insert_attributes])
                values.extend([attributes[key] for key in insert_attributes])
                values.append(object_.id)
                query.append(f'UPDATE data.{current_class.name} SET {str_update} WHERE id = %s;')

        # Query ausführen
        cursor = self.get_connection().cursor()
        cursor.execute('\n'.join(query), tuple(values))

    def bind(self, origin: Object, target: Object, association: Association | str, rebind: bool = False):
        """ Schafft eine Assoziation vom Ursprungs- zum Zielobjekt """
        cursor = self.get_connection().cursor()
        association_name = association.name if type(association) is Association else association
        if rebind:
            cursor.execute(f'DELETE FROM association.{association_name} WHERE origin_id = %s', (origin.id,))
        if target is not None:
            cursor.execute(f'INSERT INTO association.{association_name} (origin_id, target_id) VALUES (%s, %s)', (origin.id, target.id))

    def unbind(self, origin: Object, target: Object, association: Association | str):
        """ Löscht eine bestehende Assoziation vom Ursprungs- zum Zielobjekt """
        cursor = self.get_connection().cursor()
        association_name = association.name if type(association) is Association else association
        cursor.execute(f'DELETE FROM association.{association_name} WHERE origin_id = %s AND target_id = %s', (origin.id, target.id))

    def hop(self, object_: Object, association: Association | str) -> list:
        """ Gibt die mit dem übergebenen Objekte über die übergebene Assoziation verbundenen Objekte zurück """
        cursor = self.get_connection().cursor()
        if type(association) is str:
            association = self.get_association_by_name(association)
        cursor.execute(f'SELECT target_id FROM association.{association.name} WHERE origin_id = %s', (object_.id,))
        return [self.get_object(row[0], association.get_target_class()) for row in cursor.fetchall()]

    def hop1(self, object_: Object, association: Association | str) -> Object:
        """ Gibt das erste mit dem übergebenen Objekte über die übergebene Assoziation verbundene Objekt zurück """
        cursor = self.get_connection().cursor()
        if type(association) is str:
            association = self.get_association_by_name(association)
        cursor.execute(f'SELECT target_id FROM association.{association.name} WHERE origin_id = %s', (object_.id,))
        return self.get_object(cursor.fetchone()[0], association.get_target_class())

    ################################################## Berechtigung ##################################################
    def create_group(self, name: str, parent: Group = None) -> Group:
        """ Erstellt eine neue Benutzergruppe mit dem übergebenen Namen und gibt ein Group-Objekt zurück """
        cursor = self.get_connection().cursor()
        if parent:
            cursor.execute('INSERT INTO permission.group (name, parent_id) VALUES (%s, %s) RETURNING id', (name, parent.id))
        else:
            cursor.execute('INSERT INTO permission.group (name) VALUES (%s) RETURNING id', (name,))
        return Group(self, cursor.fetchone()[0], name, parent.id if parent else None)
        
    def assign_user_to_group(self, user: User, group: Group):
        """ Weist den übergebenen Benutzer der übergebenen Benutzergruppe zu """
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO permission.user_assignment (user_id, group_id) VALUES (%s, %s)', (user.id, group.id))

    def assign_object_to_group(self, object: Object, group: Group):
        """ Weist das übergebene Object der übergebenen Benutzergruppe zu """
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO permission.object_assignment (object_id, group_id) VALUES (%s, %s)', (object.id, group.id))

    def assign_association_to_group(self, association: Association, group: Group):
        """ Weist die übergeben Assoziation der übergebenen Benutzergruppe zu """
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO permission.association_assignment (association_id, group_id) VALUES (%s, %s)', (association.id, group.id))