from typing import Optional

from pydantic import BaseModel, Field, model_validator, field_validator

from dmdoc.core.sink.data_type import EnumValue, DataType


class DocumentationMixin(BaseModel):
    aliases: list[str] = Field(description="Additional names or identifiers", default=[])
    doc: Optional[str] = Field(description="Documentation string", default=None)


class DataModel(BaseModel):
    id: str = Field(description="Unique identifier", pattern="[A-Za-z_][A-Za-z0-9_]*")
    name: Optional[str] = Field(description="User friendly name", default=None)
    doc: Optional[str] = Field(description="Documentation string", default=None)
    entities: dict[str, "Entity"] = Field(description="List of entities belonging to the data model", min_length=1)
    objects: dict[str, "DataModelObject"] = Field(description="Objects shared between entities", default={})
    enums: dict[str, "DataModelEnum"] = Field(description="List of enum types shared between entities", default={})

    @model_validator(mode="after")
    def validate_references(self):
        for _id, entity in self.entities.items():
            for reference in entity.references:
                if (referenced_entity := self.entities.get(reference.id_entity)) is None:
                    raise ValueError(f"Entity `{_id}` reference an entity that does not exists `{reference.id_entity}`")
                for mapping in reference.mapping:
                    if not is_valid_field_path(mapping.source, entity.fields, self.objects):
                        raise ValueError(f"Source field {mapping.source} is not valid for entity {_id}")
                    if not is_valid_field_path(mapping.destination, referenced_entity.fields, self.objects):
                        raise ValueError(f"Target field {mapping.destination} is not valid for entity {_id}")
        return self


class BaseObject(DocumentationMixin):
    fields: dict[str, "ModelField"] = Field(description="List of fields", min_length=1)

    # noinspection PyNestedDecorators
    @field_validator("fields")
    @classmethod
    def check_unique_names(cls, fields: dict[str, "ModelField"]) -> dict[str, "ModelField"]:
        seen_ids = set()
        duplicates = [f for f in fields.values() if f.name in seen_ids or seen_ids.add(f.name)]
        if len(duplicates):
            raise ValueError(f"Duplicated fields identifiers are not allowed: {duplicates}")
        return fields


class DataModelEnum(DocumentationMixin):
    values: set["EnumValue"] = Field(description="List of allowed values", min_length=1)


class DataModelObject(BaseObject):
    pass


class Entity(BaseObject):
    references: list["EntityReference"] = Field(description="External references to other entities", default=[])


class EntityReference(BaseModel):
    id_entity: str = Field(description="Referenced entity")
    name: Optional[str] = Field(description="Reference name", default=None)
    mapping: list["FieldReference"] = Field(description="References")


class FieldReference(BaseModel):
    source: str = Field(description="Source field name")
    destination: str = Field(description="Target field name")


class ModelField(BaseModel):
    name: str = Field(description="Field name")
    type: "DataType" = Field(description="Field data type")
    doc: Optional[str] = Field(description="Documentation string", default=None)
    is_key: bool = Field(description="Whether the field is part of key or not", default=False)
    is_required: bool = Field(description="Whether the field is required or not", default=False)

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def parse_type(cls, model) -> dict:
        if isinstance(model, dict):
            value = model.get("type")
            if isinstance(value, str):
                return model | {"type": {"type": value}}
        return model


def get_python_class_id(python_class: type) -> str:
    return f"{python_class.__module__}.{python_class.__name__}"


def find_reversed_references(id_entity: str, data_model: DataModel) -> dict[str, list[EntityReference]]:
    """ Find all entities that reference the provided entity """

    references: dict[str, list[EntityReference]] = {}
    for _id, entity in data_model.entities.items():
        if not entity.references:
            continue
        current_references = []
        for reference in entity.references:
            if reference.id_entity == id_entity:
                current_references.append(reference)
        if current_references:
            references[_id] = current_references
    return references


def is_valid_field_path(
        field_path: str,
        fields: dict[str, "ModelField"],
        available_objects: dict[str, "DataModelObject"],
        prefixes: list[str] = None
) -> bool:
    """ Returns true if the field path is valid """

    for _id, field in fields.items():
        _current_field_path = (prefixes or []) + [_id]
        if (current_field_path := ".".join(_current_field_path)) == field_path:
            return True
        if (
                field_path.startswith(current_field_path) and
                _is_valid_field_path(field_path, field.type, available_objects, _current_field_path)
        ):
            return True
    return False


def _is_valid_field_path(
        field_path: str,
        data_type: DataType,
        available_objects: dict[str, "DataModelObject"],
        prefixes: list[str] = None
):
    nested_object = None
    if data_type.type == "object":
        nested_object = available_objects[data_type.id]
    elif data_type.type == "array" and data_type.items.type == "object":
        nested_object = available_objects[data_type.items.id]
    elif data_type.type == "map" and data_type.values.type == "object":
        nested_object = available_objects[data_type.values.id]
    elif data_type.type == "union":
        for _type in data_type.types:
            if _is_valid_field_path(field_path, data_type, available_objects, prefixes):
                return True
    if (
            nested_object is not None and
            is_valid_field_path(field_path, nested_object.fields, available_objects, prefixes)
    ):
        return True
