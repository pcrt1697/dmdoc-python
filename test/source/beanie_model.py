from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Optional, Union

from beanie import Document
from pydantic import BaseModel, Field

from dmdoc.core.sink.model import EntityReference, FieldReference
from dmdoc.core.sink.util import get_python_class_id


class SampleEnum(StrEnum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"


class ReferencedDocument(Document):
    pass


class NestedObject(BaseModel):
    string_field: str


class SampleDocument(Document, title="Sample docstring"):
    string_field: str = Field(description="Sample description")
    bool_field: bool | None
    bytes_field: bytes
    float_field: float
    decimal_field: Decimal
    integer_field: int
    datetime_field: datetime
    date_field: date
    time_field: time
    enum_field: SampleEnum
    union_field: Union[str, int]
    optional_field: Optional[str]
    map_field: dict[str, str]
    list_array_field: list[str]
    set_array_field: set[str]
    tuple_array_field: tuple[str]
    object_field: NestedObject
    mixed_array_field: list[str | int]

    class DmDocConfig:
        references = [
            EntityReference(
                id_entity=ReferencedDocument.__name__,
                mapping=[
                    FieldReference(
                        source="string_field",
                        destination="_id"
                    )
                ]
            )
        ]

    class Settings:
        name = "samples"


document_models = [SampleDocument, ReferencedDocument]
