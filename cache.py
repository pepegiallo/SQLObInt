from control import Class, Attribute, Association

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