import abc
import logging
from typing import Literal, Optional, Annotated, Union

from pydantic import BaseModel, Field, model_serializer, model_validator, TypeAdapter

from dmdoc.utils.importing import import_entrypoint_items

_logger = logging.getLogger()
_DATATYPES_ENTRYPOINTS_PATH = "dmdoc.sink.datatypes"


def generate_polymorphic_type(*types: type, discriminator: str):
    return Annotated[
        Union[*types],
        Field(discriminator=discriminator)
    ]


class BaseDataType(BaseModel, abc.ABC):
    @classmethod
    def get_type(cls):
        _type = cls.model_fields.get("type")
        if _type is None:
            raise AttributeError("Invalid data type class: `type` field is missing")
        if _type.annotation.__name__.lower() != "literal" or len(_type.annotation.__args__) != 1:
            raise AttributeError("Invalid data type class: `type` field is not a string literal")
        return _type.annotation.__args__[0]


class PrimitiveType(BaseDataType, abc.ABC):
    @model_serializer
    def serialize(self) -> str:
        # short representation
        return self.type


class BooleanDataType(PrimitiveType):
    type: Literal["boolean"] = Field(description="Type discriminator")


class IntegerDataType(PrimitiveType):
    type: Literal["integer"] = Field(description="Type discriminator")


class NumberDataType(PrimitiveType):
    type: Literal["number"] = Field(description="Type discriminator")


class BytesDataType(PrimitiveType):
    type: Literal["bytes"] = Field(description="Type discriminator")


class StringDataType(PrimitiveType):
    type: Literal["string"] = Field(description="Type discriminator")


class DateDataType(PrimitiveType):
    type: Literal["date"] = Field(description="Type discriminator")


class DatetimeDataType(PrimitiveType):
    type: Literal["datetime"] = Field(description="Type discriminator")


class TimeDataType(PrimitiveType):
    type: Literal["time"] = Field(description="Type discriminator")


class ObjectDataType(BaseDataType):
    type: Literal["object"] = Field(description="Type identifier")
    id: str = Field(description="Object identifier")


class EnumDataType(BaseDataType):
    type: Literal["enum"] = Field(description="Type identifier")
    id: str = Field(description="Enum identifier")


class EnumValue(BaseModel):
    name: str = Field(description="User friendly value name")
    value: str = Field(description="Value identifier that must match the regex: [A-Za-z0-9_]*")
    doc: Optional[str] = Field(description="Documentation string", default=None)

    def __hash__(self):
        return self.value.__hash__()


class ArrayDataType(BaseDataType):
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


class MapDataType(BaseDataType):
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


class UnionDataType(BaseDataType):
    type: Literal["union"] = Field(description="Type identifier")
    types: list["DataType"] = Field(description="Data types", min_length=2)


class ObjectIdDataType(BaseDataType):
    type: Literal["objectId"] = Field(description="Type discriminator")


def _add_beanie_extra_data_types(types: dict[str, type["DataType"]]):
    try:
        from dmdoc.core.source.beanie_source import BeanieSource
        _objectid_type_name = ObjectIdDataType.get_type()
        if _objectid_type_name in types:
            raise Exception(
                f"Cannot configure `{_objectid_type_name}` data type: "
                f"an entry point class [{types[_objectid_type_name]}] already exists with that name"
            )
        types[_objectid_type_name] = ObjectIdDataType
    except ImportError:
        _logger.debug("Skipping beanie source data types registration...")


def _generate_datatype():
    types: dict[str, type["DataType"]] = import_entrypoint_items(_DATATYPES_ENTRYPOINTS_PATH)
    _add_beanie_extra_data_types(types)

    for type_name, type_class in types.items():
        if not issubclass(type_class, BaseDataType):
            raise ValueError(f"Invalid type `{type_name}`: class does not inherit from {DataType}")
        class_type = type_class.get_type()
        if type_name != class_type:
            raise AttributeError(
                f"Invalid type `{type_name}`: class type {type_class.get_type()} does not match the declared type"
            )
    return generate_polymorphic_type(
        *types.values(),
        discriminator="type"
    )


def create_datatype(**kwargs) -> "DataType":
    return _datatype.validate_python(kwargs)


DataType = _generate_datatype()
_datatype = TypeAdapter(DataType)
