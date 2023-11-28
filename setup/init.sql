-- Schema Struktur: Enthält Tabellen zur objektorientierten und hierarchischen Datenstruktur
CREATE SCHEMA structure;

-- Klasse
CREATE TABLE structure.class (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    parent_id UUID REFERENCES structure.class(id)
);
CREATE INDEX class_name ON structure.class(name);

-- Attribut
CREATE TABLE structure.attribute (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    generator TEXT NOT NULL,
    indexed BOOLEAN NOT NULL
);
CREATE INDEX attribute_name ON structure.attribute(name);

-- Attributzuweisung: Zuweisung von Attributen zu Klassen
CREATE TABLE structure.attribute_assignment (
    class_id UUID REFERENCES structure.class(id),
    attribute_id UUID REFERENCES structure.attribute(id),
    nullable BOOLEAN NOT NULL,
    "default" VARCHAR(64),
    PRIMARY KEY (class_id, attribute_id)
);

-- Referenz: Verknüpfungen zwischen Objekten, Referenzen können nur zwischen zwei definierten Objektklassen bestehen
CREATE TABLE structure.reference (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    origin_class_id UUID REFERENCES structure.class(id),
    target_class_id UUID REFERENCES structure.class(id)
);
CREATE INDEX reference_name ON structure.reference(name);

-- Schema Berechtigungen: Enthält Tabellen zur Verwaltung von Benutzern und Berechtigungsgruppen
CREATE SCHEMA permission;

CREATE TABLE permission.user (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    external_id UUID UNIQUE,
    created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX user_name ON permission.user(name);
CREATE INDEX user_external_id ON permission.user(external_id);

CREATE TABLE permission.group (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(64) UNIQUE NOT NULL,
    parent_id UUID REFERENCES permission.group(id)
);
CREATE INDEX group_name ON permission.group(name);

CREATE TABLE permission.user_assignment (
    user_id UUID REFERENCES permission.user(id),
    group_id UUID REFERENCES permission.group(id),
    PRIMARY KEY (user_id, group_id)
);

CREATE TABLE permission.class_assignment (
    class_id UUID REFERENCES structure.class(id),
    group_id UUID REFERENCES permission.group(id),
    "read" BOOLEAN NOT NULL,
    write BOOLEAN NOT NULL,
    "delete" BOOLEAN NOT NULL,
    administration BOOLEAN NOT NULL,
    PRIMARY KEY (class_id, group_id)
);

CREATE TABLE permission.reference_assignment (
    reference_id UUID REFERENCES structure.reference(id),
    group_id UUID REFERENCES permission.group(id),
    "read" BOOLEAN NOT NULL,
    write BOOLEAN NOT NULL,
    "delete" BOOLEAN NOT NULL,
    administration BOOLEAN NOT NULL,
    PRIMARY KEY (reference_id, group_id)
);

-- Schema Referenzen: Enthält eine Tabelle für jede definierte Referenz, in welcher die Verbindungen zwischen Objekten abgelegt sind
CREATE SCHEMA reference;

-- Schema Daten: Enthält eine Tabelle für jede Objektklasse, in welcher die Daten abgelegt werden sowie eine Meta-Tabelle mit Grundlegenden Informationen zu jeden Objekt
CREATE SCHEMA data;

CREATE TABLE data.meta (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    class_id UUID REFERENCES structure.class(id),
    creator_id UUID REFERENCES permission.user(id),
    created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Objektzuweising zu einer Benutzergruppe: Kann aufgrund des Fremdschlüssels erst nach dem Definieren der Meta-Tabelle erzeugt werden
CREATE TABLE permission.object_assignment (
    object_id UUID REFERENCES data.meta(id),
    group_id UUID REFERENCES permission.group(id),
    "read" BOOLEAN NOT NULL,
    write BOOLEAN NOT NULL,
    "delete" BOOLEAN NOT NULL,
    administration BOOLEAN NOT NULL,
    PRIMARY KEY (object_id, group_id)
);

-- Root-Benutzer erstellen und User-ID zurückgeben
INSERT INTO permission.user(name) VALUES ('root') RETURNING id; 