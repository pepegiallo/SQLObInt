from control import Class, Attribute, Reference, Object, Group

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
        self.reference_cache = DictCache('id', 'name')

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

    def store_reference(self, reference: Reference) -> None:
        """ Fügt ein Referenzobjekt hinzu """
        self.reference_cache.store(reference)

    def get_reference(self, attr, value) -> Class:
        """ Gibt ein Referenzobjekt anhand 'id' oder 'name' zurück """
        return self.reference_cache.get(attr, value)

    def contains_reference(self, attr, value) -> bool:
        """ Gibt anhand 'id' oder 'name' zurück, ob die Referenz im Cache vorhanden ist """
        return self.reference_cache.contains(attr, value)

class PermissionDefinition:
    def __init__(self, read: bool, write: bool, delete: bool, administration: bool) -> None:
        self.read = read
        self.write = write
        self.delete = delete
        self.administration = administration
        
class PermissionCache:
    def __init__(self) -> None:
        self.group_cache = DictCache('id', 'name')
        self.class_cache = DictCache('id', 'name')
        self.reference_cache = DictCache('id', 'name')
        self.object_cache = DictCache('id')

    def store_group(self, group: Group) -> None:
        """ Fügt eine Benutzergruppe hinzu """
        self.group_cache.store(group)

    def get_group(self, attr, value) -> Group:
        """ Gibt eine Benutzergruppe anhand 'id' oder 'name' zurück """
        return self.group_cache.get(attr, value)

    def contains_group(self, attr, value) -> bool:
        """ Gibt anhand 'id' oder 'name' zurück, ob die Benutzergruppe im Cache vorhanden ist """
        return self.group_cache.contains(attr, value)

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
    
    def store_reference_permissions(self, reference: Reference, read: bool, write: bool, delete: bool, administration: bool):
        """ Fügt die Berechtigungsdefinition einer Referenz hinzu """
        self.reference_cache.store_custom(
            PermissionDefinition(read, write, delete, administration),
            id=reference.id,
            name=reference.name
        )
    
    def get_reference_permissions(self, attr, value) -> PermissionDefinition:
        """ Gibt die Berechtigungsdefinition einer Referenz anhand von 'id' oder 'name' zurück """
        return self.reference_cache.get(attr, value)

    def contains_reference_permissions(self, attr, value) -> bool:
        """ Gibt anhand von 'id' oder 'name' zurück, ob die Berechtigungsdefinition der Referenz im Cache vorhanden ist """
        return self.reference_cache.contains(attr, value)
    
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
