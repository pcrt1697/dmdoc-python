from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from typing import Type, Iterable, Optional

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from dmdoc.core.sink.data_type import create_datatype, EnumValue
from dmdoc.core.sink.model import DataModel, Entity, ModelField, DataModelObject, DataModelEnum
from dmdoc.core.sink.util import get_python_class_id
from dmdoc.core.source import Source
from dmdoc.utils.exception import DataTypeResolutionError
from dmdoc.utils.importing import import_object


def _get_doc_from_model_class(model_class: type[BaseModel]):
    return model_class.model_config.get("title")


def _get_references_from_model_class(model_class: type[BaseModel]):
    if hasattr(model_class, "DmDocConfig"):
        config = model_class.DmDocConfig
        if hasattr(config, "references"):
            return config.references
    return []


def get_collection_name(document_class: type[Document]):
    if hasattr(document_class, "Settings") and hasattr(document_class.Settings, "name"):
        return document_class.Settings.name
    return document_class.__name__


class BeanieSourceConfig(BaseModel):
    id: str = Field(description="Unique identifier", pattern="[A-Za-z_][A-Za-z0-9_]*")
    name: Optional[str] = Field(description="User friendly name", default=None)
    doc: Optional[str] = Field(description="Documentation string", default=None)
    classes: str = Field(
        description="Path to an iterable of document classes (extending `beanie.Document`) "
                    "defined as <package-path>:<iterable-name>"
    )


class BeanieSource(Source):
    _config: BeanieSourceConfig

    @classmethod
    def get_config_class(cls) -> Type[BaseModel]:
        return BeanieSourceConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._objects: dict[str, "DataModelObject"] = {}
        self._enums: dict[str, "DataModelEnum"] = {}

    def _do_generate(self) -> DataModel:
        document_classes: Iterable[type[Document]] = import_object(self._config.classes)
        if not isinstance(document_classes, Iterable):
            raise ValueError(
                f"Classes iterable {self._config.classes} is not an iterable"
            )

        entities = {}
        for model_class in document_classes:
            if not issubclass(model_class, Document):
                raise ValueError(
                    f"Document class {model_class} must inherit from {Document}"
                )
            entities[get_collection_name(model_class)] = self._convert_entity(model_class)
        return DataModel(
            id=self._config.id,
            name=self._config.name,
            doc=self._config.doc,
            entities=entities,
            objects=self._objects,
            enums=self._enums
        )

    def _convert_map(self, annotation_args: set):
        if len(annotation_args) != 1:
            raise DataTypeResolutionError(
                f"Map conversion failed: expected exactly one annotation argument, found {annotation_args}"
            )
        return create_datatype(
            type="map",
            values=self._resolve_type(annotation_args.pop())
        )

    def _convert_enum(self, enum_class: type[Enum]):
        full_name = get_python_class_id(enum_class)
        self._enums[enum_class.__name__] = DataModelEnum(
            aliases=[full_name],
            values={
                EnumValue(
                    value=str(value.value)
                )
                for value in enum_class
            }
        )
        return create_datatype(
            type="enum",
            id=enum_class.__name__
        )

    def _convert_array(self, annotation_args: set):
        if len(annotation_args) != 1:
            raise DataTypeResolutionError(f"Expected exactly one annotation argument, found [{annotation_args}]")
        elif len(annotation_args) == 1:
            items_type = self._resolve_type(annotation_args.pop())
        else:
            items_type = self._convert_union(annotation_args)
        return create_datatype(
            type="array",
            items=items_type
        )

    def _convert_union(self, annotations: set):
        if len(annotations) == 0:
            raise DataTypeResolutionError(f"Expected at least one annotation, found {annotations}")
        elif len(annotations) == 1:
            return self._resolve_type(annotations.pop())

        return create_datatype(
            type="union",
            types=[
                self._resolve_type(annotation)
                for annotation in annotations
            ]
        )

    def _convert_object(self, python_class: type[BaseModel]):
        full_name = get_python_class_id(python_class)
        self._objects[python_class.__name__] = DataModelObject(
            aliases=[full_name],
            fields=self._extract_fields(python_class),
            doc=_get_doc_from_model_class(python_class),
            references=_get_references_from_model_class(python_class)
        )
        return create_datatype(
            type="object",
            id=python_class.__name__
        )

    def _create_type_from_python_class(self, python_class: type):
        if python_class == str:
            return create_datatype(type="string")
        if python_class == int:
            return create_datatype(type="integer")
        if python_class == bool:
            return create_datatype(type="boolean")
        if python_class == float or python_class == Decimal:
            return create_datatype(type="number")
        if python_class == datetime:
            return create_datatype(type="datetime")
        if python_class == date:
            return create_datatype(type="date")
        if python_class == time:
            return create_datatype(type="time")
        if python_class == bytes:
            return create_datatype(type="bytes")

        if python_class == PydanticObjectId:
            return create_datatype(type="objectId")

        if isinstance(python_class, type):
            if issubclass(python_class, Enum):
                return self._convert_enum(python_class)
            if issubclass(python_class, BaseModel):
                return self._convert_object(python_class)

        raise DataTypeResolutionError(f"Cannot resolve data type for python class {python_class}")

    def _resolve_type(self, annotation):
        if isinstance(annotation, type):
            return self._create_type_from_python_class(annotation)

        # noinspection PyUnresolvedReferences
        annotation_args = set(annotation.__args__)
        annotation_args.discard(type(None))
        if hasattr(annotation, "__name__"):
            annotation_name = annotation.__name__
        else:
            annotation_name = annotation.__class__.__name__
        annotation_name = annotation_name.lower()
        match annotation_name:
            case "dict":
                return self._convert_map(annotation_args)
            case "list" | "set" | "tuple":
                return self._convert_array(annotation_args)
            case "union" | "uniontype":
                return self._convert_union(annotation_args)

        if len(annotation_args) != 1:
            raise DataTypeResolutionError(f"Expected exactly one annotation argument, found [{annotation_args}]")

        return self._create_type_from_python_class(annotation_args.pop())

    def _extract_fields(self, model_class: type[BaseModel]):
        fields = []
        for _id, field_info in model_class.model_fields.items():
            if field_info.exclude:
                # e.g. revision_id
                continue
            try:
                data_type = self._resolve_type(field_info.annotation)
            except Exception as e:
                raise DataTypeResolutionError(f"Failed to resolve type for field `{_id}`") from e
            fields.append(
                ModelField(
                    id=_id,
                    type=data_type,
                    doc=field_info.description,
                    is_required=field_info.is_required()
                )
            )
        return fields

    def _convert_entity(self, model_class: type[Document]):
        fields = self._extract_fields(model_class)
        return Entity(
            aliases=[get_python_class_id(model_class)],
            doc=_get_doc_from_model_class(model_class),
            fields=fields,
            references=_get_references_from_model_class(model_class)
        )
