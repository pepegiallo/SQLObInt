class User:
    def __init__(self, id: str):
        self.id = id

class Class:
    def __init__(self, interface, id: str, name: str, parent_id: str) -> None:
        self.interface = interface
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.assigned_attributes = None
        interface.structure_cache.store_class(self)

    def get_parent(self):
        """ Gibt Klassenobjekt der Parent-Klasse zurück """
        return self.interface.get_class_by_id(self.parent_id)

    def get_family_tree(self) -> list:
        """ Gibt den Stammbaum der Klasse (alle übergeordneten Klassen und sich selbst) zurück """
        if self.is_root():
          return [self]
        else:
          family_tree = self.get_parent().get_family_tree()
          family_tree.append(self)
          return family_tree

    def get_assigned_attributes(self):
        """ Gibt die der Klasse direkt zugewiesenen Attribute zurück """
        if not self.assigned_attributes:
            self.assigned_attributes = self.interface.get_assigned_attributes_from_db(self)
        return self.assigned_attributes

    def is_root(self):
        """ Gibt zurück, ob die Klasse eine Ursprungsklasse ist (keine Vorfahren hat) """
        return self.parent_id is None

    def get_view_name(self):
        """ Gibt den Namen der View in der Datenbank zum Anzeigen aller Objekte der Klasse zurück """
        return f'v_{self.name}'

    def update_view(self):
        """ Erstellt oder aktualisiert in der Datenbank eine View zum Anzeigen aller Objekte der Klasse """
        self.interface.update_class_view(self)


class Attribute:
    def __init__(self, interface, id: str, name: str, generator: str, indexed: bool) -> None:
        self.interface = interface
        self.id = id
        self.name = name
        self.generator = generator
        self.indexed = indexed
        interface.structure_cache.store_attribute(self)

class AttributeAssignment:
    def __init__(self, interface, class_id: str, attribute_id: str, nullable: bool, default: str):
        self.interface = interface
        self.class_id = class_id
        self.attribute_id = attribute_id
        self.nullable = nullable
        self.default = default

    def get_class(self) -> Class:
        """ Gibt Klassenobjekt zurück """
        return self.interface.get_class_by_id(self.class_id)

    def get_attribute(self) -> Attribute:
        """ Gibt Attributobjekt zurück """
        return self.interface.get_attribute_by_id(self.attribute_id)

class Association:
    def __init__(self, interface, id: str, name: str, origin_class_id: str, target_class_id: str) -> None:
        self.interface = interface
        self.id = id
        self.name = name
        self.origin_class_id = origin_class_id
        self.target_class_id = target_class_id
        interface.structure_cache.store_association(self)

    def get_origin_class(self):
        """ Gibt Klassenobjekt der Ursprungsklasse zurück """
        return self.interface.get_class_by_id(self.origin_class_id)

    def get_target_class(self):
        """ Gibt Klassenobjekt der Zielklasse zurück """
        return self.interface.get_class_by_id(self.target_class_id)

class Object:
    def __init__(self, interface, id: str, class_: Class, **attributes):
        self.interface = interface
        self.id = id
        self.class_ = class_
        self.attributes = attributes

    def get_class(self) -> Class:
        """ Gibt die Klasse des Objekts zurück """
        return self.class_

    def modify(self, **attributes):
        """ Aktualisiert die übergebenen Attribute """
        self.interface.modify(self, **attributes)

    def dump(self):
        """ Gibt String mit allen Objekteigenschaften zurück """
        str_attributes = '\n  '.join(f'{attribute} = {value}' for attribute, value in self.attributes.items())
        return f'{self.class_.name} {self.id}:\n  {str_attributes}'
    
class Group:
    def __init__(self, interface, id: str, name: str, parent_id: str) -> None:
        self.interface = interface
        self.id = id
        self.name = name
        self.parent_id = parent_id

    def assign_user(self, user: User):
        """ Weist den übergebenen Benutzer der Benutzergruppe zu """
        self.interface.assign_user_to_group(user, self)

    def assign_class(self, class_: Class, read: bool = False, write: bool = False, delete: bool = False, administration: bool = False):
        """ Weist das übergebene Klasse der Benutzergruppe zu """
        self.interface.assign_class_to_group(class_, self, read, write, delete, administration)

    def assign_object(self, object: Object, read: bool = False, write: bool = False, delete: bool = False, administration: bool = False):
        """ Weist das übergebene Object der Benutzergruppe zu """
        self.interface.assign_object_to_group(object, self, read, write, delete, administration)

    def assign_attribute(self, attribute: Attribute, read: bool = False, write: bool = False, delete: bool = False, administration: bool = False):
        """ Weist das übergebene Attribut der Benutzergruppe zu """
        self.interface.assign_attribute_to_group(attribute, self, read, write, delete, administration)

    def assign_association(self, association: Association, read: bool = False, write: bool = False, delete: bool = False, administration: bool = False):
        """ Weist die übergeben Assoziation der Benutzergruppe zu """
        self.interface.assign_association_to_group(association, self, read, write, delete, administration)