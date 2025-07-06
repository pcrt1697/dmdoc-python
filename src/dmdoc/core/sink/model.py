from typing import Optional

from pydantic import BaseModel, Field, model_validator, field_validator

from dmdoc.core.sink.data_type import EnumValue, DataType


def parse_type(model) -> dict:
    if isinstance(model, dict):
        value = model.get("type")
        if isinstance(value, str):
            return model | {"type": {"type": value}}
    return model


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


class BaseObject(DocumentationMixin):
    fields: list["ModelField"] = Field(description="List of fields", min_length=1)
    references: list["EntityReference"] = Field(description="External references to other entities", default=[])

    # noinspection PyNestedDecorators
    @field_validator("fields")
    @classmethod
    def check_unique_fields(cls, fields: list["ModelField"]) -> list["ModelField"]:
        seen_ids = set()
        duplicates = [f for f in fields if f.id in seen_ids or seen_ids.add(f.id)]
        if len(duplicates):
            raise ValueError(f"Duplicated fields identifiers are not allowed: {duplicates}")
        return fields


class DataModelEnum(DocumentationMixin):
    values: set["EnumValue"] = Field(description="List of allowed values", min_length=1)
    used_by: list[str] = Field(description="Entities or objects that uses this object", default=[])


class DataModelObject(BaseObject):
    used_by: list[str] = Field(description="Entities or objects that uses this object", default=[])


class Entity(BaseObject):
    referenced_by: list[str] = Field(description="Entities that references this entity", default=[])


class EntityReference(BaseModel):
    id_entity: str = Field(description="Referenced entity")
    name: Optional[str] = Field(description="Reference name", default=None)
    mapping: list["FieldReference"] = Field(description="References")


class FieldReference(BaseModel):
    source: str = Field(description="Source field name")
    destination: str = Field(description="Target field name")


class ModelField(BaseModel):
    id: str = Field(description="Unique identifier")
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
