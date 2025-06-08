import logging
from typing import Type, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Column, Table, ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase, registry

from dmdoc.core.sink.model import DataModel, Entity, ModelField, EntityReference, FieldReference
from dmdoc.core.source import Source
from dmdoc.utils.importing import import_object

_logger = logging.getLogger(__name__)


def get_class_table_mapping(mapper_registry: registry):
    # todo: test polymorphic classes
    mapping: dict[str, set[str]] = {}
    # noinspection PyProtectedMember
    for c in mapper_registry._class_registry.values():
        if not hasattr(c, "__tablename__"):
            continue
        table_name = getattr(c, "__tablename__")
        full_cls_name = f"{c.__module__}:{c.__name__}"
        if table_name in mapping:
            mapping[table_name].add(full_cls_name)
        else:
            mapping[table_name] = {full_cls_name}
    return mapping


def get_field_info(column: Column, is_key: bool) -> ModelField:
    return ModelField(
        id=column.name,
        doc=column.description,
        type="string",
        is_key=is_key,
        is_required=column.nullable
    )


def get_entity_info(table: Table, aliases: set[str]) -> Entity:
    fields = [
        get_field_info(c, table.primary_key.contains_column(c))
        for c in table.c.values()
    ]
    references = [
        get_entity_reference(fk)
        for fk in table.foreign_key_constraints
    ]
    return Entity(
        id=table.name,
        aliases=aliases,
        doc=table.description,
        fields=fields,
        references=references
    )


def get_entity_reference(fkc: ForeignKeyConstraint) -> EntityReference:
    mapping = [
        FieldReference(
            source=fk.parent.name,
            destination=fk.column.name
        )
        for fk in fkc.elements
    ]
    return EntityReference(
        id_entity=fkc.referred_table.name,
        name=fkc.name,
        mapping=mapping
    )


class SQLAlchemySourceConfig(BaseModel):
    base: str = Field(
        description="Path to the ORM base class (extending `sqlalchemy.orm.DeclarativeBase`) for declarative mapping or"
                    " `sqlalchemy.orm.registry` instance for imperative mapping, both defined as <package-path>:<name>"
    )
    id: Optional[str] = Field(
        description="Unique identifier of the data model, required when the schema is not available from the code",
        pattern="[A-Za-z_][A-Za-z0-9_]*",
        default=None
    )
    name: Optional[str] = Field(description="Name of the data model", default=None)
    doc: Optional[str] = Field(description="Documentation string", default=None)


class SQLAlchemySource(Source):
    _config: SQLAlchemySourceConfig

    @classmethod
    def get_config_class(cls) -> Type[BaseModel]:
        return SQLAlchemySourceConfig

    def _do_process(self) -> DataModel:
        base: type[DeclarativeBase] | registry = import_object(self._config.base)
        if isinstance(base, type) and issubclass(base, DeclarativeBase):
            # declarative mapping
            mapper_registry = base.registry
        elif not isinstance(base, type) and isinstance(base, registry):
            # imperative mapping
            mapper_registry = base
        else:
            raise ValueError(
                f"Base object {self._config.base} is not a subclass of {DeclarativeBase} nor an instance of {registry}"
            )
        _id = self._config.id or base.metadata.schema
        cls_names = get_class_table_mapping(mapper_registry)
        entities = []
        for table_name, table in base.metadata.tables.items():
            entity = get_entity_info(table, cls_names.get(table_name, []))
            entities.append(entity)
        return DataModel(
            id=_id,
            name=self._config.name or _id,
            doc=self._config.doc,
            entities=entities
        )
