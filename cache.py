from control import Class, Attribute, Association, Object

class DictCache:
    def __init__(self, *atts):
        self.atts = atts
        self.dicts = {}
        self.setup()

    def setup(self):
        """ Initialisiert die benötigten Dictionaries """
        for a in self.atts:
            self.dicts[a] = {}

    def store(self, element) -> None:
        """ Legt ein Element in den Dictionaries ab """
        for a in self.atts:
            self.dicts[a][getattr(element, a)] = element

    def store_custom(self, element, **kv) -> None:
        """ Legt ein Element mit den gegebenen Keys in den Dictionaries ab """
        for key, value in kv.items():
            if key in self.atts:
                self.dicts[key][value] = element

    def get(self, attr, value):
        """ Gibt ein Element anhand des übergebenen Attribut-Wert-Paares zurück """
        return self.dicts[attr].get(value)

    def contains(self, attr, value) -> bool:
        """ Gibt zurück, ein Element mit dem übergebenen Attribut-Wert-Paares vorhanden ist """
        return value in self.dicts[attr]

class StructureCache:
    def __init__(self) -> None:
        self.class_cache = DictCache('id', 'name')
        self.attribute_cache = DictCache('id', 'name')
        self.association_cache = DictCache('id', 'name')

    def store_class(self, class_: Class) -> None:
        """ Fügt ein Klassenobjekt hinzu """
        self.class_cache.store(class_)

    def get_class(self, attr, value) -> Class:
        """ Gibt ein Klassenobjekt anhand 'id' oder 'name' zurück """
        return self.class_cache.get(attr, value)

    def contains_class(self, attr, value) -> bool:
        """ Gibt anhand 'id' oder 'name' zurück, ob die Klasse im Cache vorhanden ist """
        return self.class_cache.contains(attr, value)

    def store_attribute(self, attribute: Attribute) -> None:
        """ Fügt ein Attributobjekt hinzu """
        self.attribute_cache.store(attribute)

    def get_attribute(self, attr, value) -> Class:
        """ Gibt ein Attributobjekt anhand 'id' oder 'name' zurück """
        return self.attribute_cache.get(attr, value)

    def contains_attribute(self, attr, value) -> bool:
        """ Gibt anhand 'id' oder 'name' zurück, ob das Attribut im Cache vorhanden ist """
        return self.attribute_cache.contains(attr, value)

    def store_association(self, association: Association) -> None:
        """ Fügt ein Assoziationsobjekt hinzu """
        self.association_cache.store(association)

    def get_association(self, attr, value) -> Class:
        """ Gibt ein Assoziationsobjekt anhand 'id' oder 'name' zurück """
        return self.association_cache.get(attr, value)

    def contains_association(self, attr, value) -> bool:
        """ Gibt anhand 'id' oder 'name' zurück, ob die Assoziation im Cache vorhanden ist """
        return self.association_cache.contains(attr, value)

class PermissionDefinition:
    def __init__(self, read: bool, write: bool, delete: bool, administration: bool) -> None:
        self.read = read
        self.write = write
        self.delete = delete
        self.administration = administration
        
class PermissionCache:
    def __init__(self) -> None:
        self.class_cache = DictCache('id', 'name')
        self.association_cache = DictCache('id', 'name')
        self.object_cache = DictCache('id')

    def store_class_permissions(self, class_: Class, read: bool, write: bool, delete: bool, administration: bool):
        """ Fügt die Berechtigungsdefinition einer Klasse hinzu """
        self.class_cache.store_custom(
            PermissionDefinition(read, write, delete, administration),
            id=class_.id,
            name=class_.name
        )
    
    def get_class_permissions(self, attr, value) -> PermissionDefinition:
        """ Gibt die Berechtigungsdefinition einer Klasse anhand von 'id' oder 'name' zurück """
        return self.class_cache.get(attr, value)

    def contains_class_permissions(self, attr, value) -> bool:
        """ Gibt anhand von 'id' oder 'name' zurück, ob die Berechtigungsdefinition der Klasse im Cache vorhanden ist """
        return self.class_cache.contains(attr, value)
    
    def store_association_permissions(self, association: Association, read: bool, write: bool, delete: bool, administration: bool):
        """ Fügt die Berechtigungsdefinition einer Assoziation hinzu """
        self.association_cache.store_custom(
            PermissionDefinition(read, write, delete, administration),
            id=association.id,
            name=association.name
        )
    
    def get_association_permissions(self, attr, value) -> PermissionDefinition:
        """ Gibt die Berechtigungsdefinition einer Assoziation anhand von 'id' oder 'name' zurück """
        return self.association_cache.get(attr, value)

    def contains_association_permissions(self, attr, value) -> bool:
        """ Gibt anhand von 'id' oder 'name' zurück, ob die Berechtigungsdefinition der Assoziation im Cache vorhanden ist """
        return self.association_cache.contains(attr, value)
    
    def store_object_permissions(self, object: Object, read: bool, write: bool, delete: bool, administration: bool):
        """ Fügt die Berechtigungsdefinition eine Objekts hinzu """
        self.object_cache.store_custom(
            PermissionDefinition(read, write, delete, administration),
            id=object.id
        )
    
    def get_object_permissions(self, id) -> PermissionDefinition:
        """ Gibt die Berechtigungsdefinition eines Objekts anhand von der id zurück """
        return self.object_cache.get('id', id)

    def contains_object_permissions(self, id) -> bool:
        """ Gibt anhand der id zurück, ob die Berechtigungsdefinition des Objekts im Cache vorhanden ist """
        return self.object_cache.contains('id', id)
