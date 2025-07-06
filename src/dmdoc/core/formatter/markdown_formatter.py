import logging
import os
import re
from enum import StrEnum
from typing import Type

from mdutils import MdUtils, MDList, TextUtils
from pydantic import BaseModel, Field

from dmdoc.core.formatter import Formatter
from dmdoc.core.sink.data_type import DataType, ArrayDataType, MapDataType, UnionDataType, EnumDataType, ObjectDataType
from dmdoc.core.sink.model import Entity, BaseObject, DataModelObject, DataModelEnum, DocumentationMixin

_logger = logging.getLogger(__name__)


class MDSymbol(StrEnum):
    CHECK_MARK = ":heavy_check_mark:"
    X = ":x:"


def get_local_link(header: str, text: str = None) -> str:
    """
    Creates a link to a local section of the file.
    :param header: the text of the header to be referenced
    :type text: str
    :param header: the placeholder text to display, by default `header` is used
    :type text: str
    :return: the Markdown code with the formatted link
    :rtype: str
    """
    href = "#" + re.sub("-+", "-", header.lower())
    return TextUtils.text_external_link(
        text or header,
        href
    )


def get_md_list(items: list):
    return "\n".join([f"* {item}" for item in items])


def write_aliases(md_file: MdUtils, aliases: list):
    if not aliases:
        return
    md_file.new_line("Aliases:", bold_italics_code="i")
    bullet_points = MDList([alias for alias in aliases])
    md_file.new_line(bullet_points.get_md())


class MarkdownSectionWriter:
    _model: DocumentationMixin

    def __init__(
            self,
            md_file: MdUtils,
            model: DocumentationMixin
    ):
        self._md_file = md_file
        self._model = model

    @property
    def md_file(self):
        return self._md_file

    @property
    def model(self):
        return self._model

    def write_title(self, title: str):
        self.md_file.new_header(level=2, title=title)

    def write_aliases(self):
        write_aliases(self.md_file, self.model.aliases)

    def write_description(self):
        if not self.model.doc:
            return
        self.md_file.new_paragraph(self.model.doc)


class MarkdownObjectWriter(MarkdownSectionWriter):
    _model: DataModelObject | Entity

    def write_fields(self):
        text = ["Field name", "Data type", "Required", "Description"] + [
            table_cell
            for field in self.model.fields
            for table_cell in [
                TextUtils.inline_code(field.id) if field.is_key else TextUtils.bold(field.id),
                self._type_to_text(field.type),
                MDSymbol.CHECK_MARK.value if field.is_required else " ",
                field.doc or " "
            ]
        ]
        self.md_file.new_header(level=3, title="List of fields")
        self.md_file.new_table(
            4,
            len(self.model.fields) + 1,
            text
        )

    def _type_to_text(self, data_type: DataType):
        match data_type.type:
            case "array":
                return self._array_to_text(data_type)
            case "map":
                return self._map_to_text(data_type)
            case "union":
                return self._union_to_text(data_type)
            case "enum":
                return self._enum_to_text(data_type)
            case "object":
                return self._object_to_text(data_type)
            case _:
                return data_type.type

    def _array_to_text(self, data_type: ArrayDataType):
        return f"array<{self._type_to_text(data_type.items)}>"

    def _map_to_text(self, data_type: MapDataType):
        return f"map<{self._type_to_text(data_type.values)}>"

    def _union_to_text(self, data_type: UnionDataType):
        _types = ", ".join([
            self._type_to_text(_type)
            for _type in data_type.types
        ])
        return f"union[{_types}]"

    def _enum_to_text(self, data_type: EnumDataType):
        return data_type.id

    def _object_to_text(self, data_type: ObjectDataType):
        return data_type.id

    def write_references(self):
        self.md_file.new_header(level=3, title="External references")
        items = []
        if self.model.references:
            for reference in self.model.references:
                reference_text = get_local_link(reference.id_entity)
                if reference.name is not None:
                    reference_text = f"{TextUtils.bold(reference.name)} ({reference_text})"

                items.append(reference_text)
                items.append(
                    [
                        f"{mapping.source}: {mapping.destination}"
                        for mapping in reference.mapping
                    ]
                )
        self.md_file.new_paragraph(
            MDList(items).get_md()
        )


class MarkdownEntityWriter(MarkdownObjectWriter):
    _model = Entity

    def write_referenced_by(self):
        pass


class MarkdownSharedObjectWriter(MarkdownObjectWriter):
    _model = DataModelObject

    def write_used_by(self):
        # todo: implement this
        pass


class MarkdownEnumWriter(MarkdownSectionWriter):
    _model = DataModelEnum

    def write_values(self):
        self.md_file.new_header(level=3, title="Values")
        items = []
        for value in self._model.values:
            item_text = TextUtils.bold(value.value)
            if value.doc:
                f"{item_text}: {value.doc}"
            items.append(item_text)
        self.md_file.new_paragraph(
            get_md_list(items)
        )

    def write_used_by(self):
        # todo: implement this
        pass


class MarkdownFormatterConfig(BaseModel):
    output_path: str = Field(description="Output markdown file")
    overwrite: bool = Field(description="If true, existing files will be overwritten", default=False)


class MarkdownFormatter(Formatter):

    _config: MarkdownFormatterConfig

    @classmethod
    def get_config_class(cls) -> Type[BaseModel]:
        return MarkdownFormatterConfig

    def _before_generate(self):
        if not self._config.output_path.endswith(".md"):
            raise ValueError(f"Output path must be a valid .md filepath with, received [{self._config.output_path}]")
        if os.path.isdir(self._config.output_path):
            raise ValueError(f"Output path [{self._config.output_path}] is a directory")
        if os.path.isfile(self._config.output_path):
            if not self._config.overwrite:
                raise ValueError(f"Output file already exists at [{self._config.output_path}]")
            else:
                _logger.warning("Deleting pre-existing documentation file at [%s]", self._config.output_path)
                os.remove(self._config.output_path)

    def _do_generate(self):
        # todo: raise for duplicated enum/object names
        md_file = MdUtils(
            file_name=self._config.output_path,
            title=self._data_model.name or self._data_model.id
        )
        if self._data_model.doc:
            md_file.new_paragraph(self._data_model.doc)
        self._write_entities(md_file)
        self._finalize(md_file)

    def _write_entities(self, md_file: MdUtils):
        if self._data_model.objects or self._data_model.enums:
            md_file.new_header(level=1, title="Entities")
        for name, entity in self._data_model.entities.items():
            entity_writer = MarkdownEntityWriter(
                md_file,
                entity
            )
            entity_writer.write_title(name)
            entity_writer.write_aliases()
            entity_writer.write_description()
            entity_writer.write_fields()
            entity_writer.write_references()
            entity_writer.write_referenced_by()

    def _finalize(self, md_file: MdUtils):
        self._write_objects(md_file)
        self._write_enums(md_file)

        md_file.new_table_of_contents(table_title='Index', depth=2)
        md_file.create_md_file()

    def _write_objects(self, md_file: MdUtils):
        md_file.new_header(level=1, title="Objects")
        for name, obj in self._data_model.objects.items():
            entity_writer = MarkdownSharedObjectWriter(md_file, obj)
            entity_writer.write_title(name)
            entity_writer.write_aliases()
            entity_writer.write_description()
            entity_writer.write_fields()
            entity_writer.write_references()

    def _write_enums(self, md_file: MdUtils):
        md_file.new_header(level=1, title="Enums")
        for name, obj in self._data_model.enums.items():
            entity_writer = MarkdownEnumWriter(md_file, obj)
            entity_writer.write_title(name)
            entity_writer.write_aliases()
            entity_writer.write_description()
            entity_writer.write_values()
