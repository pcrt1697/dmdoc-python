import abc
from typing import Union, Literal, Annotated, Optional, Any

from pydantic import BaseModel, Field, model_serializer, model_validator, field_validator


def generate_polymorphic_type(*types: type, discriminator: str):
    return Annotated[
        Union[*types],
        Field(discriminator=discriminator)
    ]


def parse_type(model) -> dict:
    if isinstance(model, dict):
        value = model.get("type")
        if isinstance(value, str):
            return model | {"type": {"type": value}}
    return model


class DataModel(BaseModel):
    id: str = Field(description="Unique identifier", pattern="[A-Za-z_][A-Za-z0-9_]*")
    name: Optional[str] = Field(description="User friendly name", default=None)
    doc: Optional[str] = Field(description="Documentation string", default=None)
    entities: list["Entity"] = Field(description="List of entities belonging to the data model", min_length=1)
    shared_objects: list["BaseObject"] = Field(description="List of objects types shared between entities", default=[])

    # noinspection PyNestedDecorators
    @field_validator("entities", "shared_objects")
    @classmethod
    def check_unique_entities_and_commons(
            cls,
            values: list["Entity"] | list["BaseObject"]
    ) -> list["Entity"] | list["BaseObject"]:
        seen_ids = set()
        duplicates = [v for v in values if v.id in seen_ids or seen_ids.add(v.id)]
        if len(duplicates):
            raise ValueError(f"Duplicated identifiers are not allowed: {duplicates}")
        return values


class BaseObject(BaseModel):
    id: str = Field(description="Unique identifier")
    aliases: list[str] = Field(description="Additional names or identifiers", default=[])
    doc: Optional[str] = Field(description="Documentation string", default=None)
    fields: list["ModelField"] = Field(description="List of fields", min_length=1)
    discriminator: Optional[str] = Field(description="Discriminator for subtypes", default=None)
    subtypes: Optional[list[str]] = Field(description="List of subtypes", default=None)
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

    @model_validator(mode="after")
    def validate_discriminator(self):
        if self.discriminator and not self.subtypes:
            raise ValueError("Subtypes list cannot be empty when a discriminator is provided")
        if not self.discriminator and self.subtypes:
            raise ValueError("Discriminator cannot be empty when a subtypes list is provided")
        if self.discriminator:
            for field in self.fields:
                if self.discriminator == field.id:
                    return self
        else:
            return self
        raise ValueError("Discriminator field not found in field list")


class SharedObject(BaseObject):
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


class BaseDataType(BaseModel, abc.ABC):
    pass


class PrimitiveType(BaseDataType, abc.ABC):
    @model_serializer
    def serialize(self) -> str:
        return self.type


class BooleanType(PrimitiveType):
    type: Literal["boolean"] = Field(description="Type discriminator")


class IntegerType(PrimitiveType):
    type: Literal["integer"] = Field(description="Type discriminator")


class LongType(PrimitiveType):
    type: Literal["long"] = Field(description="Type discriminator")


class FloatType(PrimitiveType):
    type: Literal["float"] = Field(description="Type discriminator")


class DoubleType(PrimitiveType):
    type: Literal["double"] = Field(description="Type discriminator")


class BytesType(PrimitiveType):
    type: Literal["bytes"] = Field(description="Type discriminator")


class StringType(PrimitiveType):
    type: Literal["string"] = Field(description="Type discriminator")


class DateType(PrimitiveType):
    type: Literal["date"] = Field(description="Type discriminator")


class DatetimeType(PrimitiveType):
    type: Literal["datetime"] = Field(description="Type discriminator")


class ComplexType(BaseDataType, abc.ABC):
    pass


class ObjectType(ComplexType, BaseObject):
    type: Literal["object"] = Field(description="Type identifier")

    @model_validator(mode="after")
    def check_reference_or_definition(self):
        # todo: check and fix this validation
        if self.fields is not None and len(self.fields) > 0:
            if self.id is not None:
                raise ValueError("Ambiguous object definition: both fields and id provided")
        elif self.id is not None:
            if self.fields is not None and len(self.fields) > 0:
                raise ValueError("Ambiguous object definition: both fields and id provided")
            self.fields = []
        else:
            raise ValueError("No fields nor id provided")
        return self


class EnumType(ComplexType):
    # todo: maybe add enum identifier and manage enums like shared objects
    type: Literal["enum"] = Field(description="Type identifier")
    values: list["EnumValue"] = Field(description="List of allowed values")
    doc: Optional[str] = Field(description="Documentation string", default=None)

    # noinspection PyNestedDecorators
    @field_validator("values")
    @classmethod
    def check_unique_values(cls, values: list["EnumValue"]) -> list["EnumValue"]:
        seen_ids = set()
        duplicates = [v for v in values if v.id in seen_ids or seen_ids.add(v.id)]
        if len(duplicates):
            raise ValueError(f"Duplicated identifiers are not allowed: {duplicates}")
        return values


class EnumValue(BaseModel):
    value: str | int = Field(description="Value identifier that must match the regex: [A-Za-z0-9_]*")
    doc: Optional[str] = Field(description="Documentation string", default=None)


class ArrayType(ComplexType):
    type: Literal["array"] = Field(description="Type identifier")
    items: "DataType" = Field(description="Data type of array items")

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def parse_type(cls, model) -> dict:
        if isinstance(model, dict):
            value = model.get("items")
            if isinstance(value, str):
                # manage primitive types
                return model | {"items": {"type": value}}
        return model


class MapType(ComplexType):
    type: Literal["map"] = Field(description="Type identifier")
    values: "DataType" = Field(description="Data type of map values")

    # noinspection PyNestedDecorators
    @model_validator(mode="before")
    @classmethod
    def parse_type(cls, model) -> dict:
        if isinstance(model, dict):
            value = model.get("values")
            if isinstance(value, str):
                # manage primitive types
                return model | {"values": {"type": value}}
        return model


class UnionType(ComplexType):
    type: Literal["union"] = Field(description="Type identifier")
    types: list["DataType"] = Field(description="Data types", min_length=2)


# todo: add support for custom types
DataType = generate_polymorphic_type(
    # primitive types
    BooleanType, IntegerType, LongType, FloatType, DoubleType, BytesType, StringType, DateType, DatetimeType,
    # complex types
    EnumType, ArrayType, MapType, UnionType, ObjectType,
    discriminator="type"
)

PRIMITIVE_TYPES = (
    "boolean", "integer", "long", "float", "double", "bytes", "string", "date", "datetime"
)
