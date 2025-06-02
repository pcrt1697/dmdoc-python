import logging
import os
import re
from enum import StrEnum
from typing import Type

from mdutils import MdUtils, MDList, TextUtils
from pydantic import BaseModel, Field

from dmdoc.core.formatter import Formatter
from dmdoc.core.sink.model import Entity, BaseObject

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


class MarkdownModelWriter:
    _model: BaseObject

    def __init__(self, md_file: MdUtils, model: BaseObject, root_level: int = 1):
        self._md_file = md_file
        self._model = model
        self._root_level = root_level

    @property
    def md_file(self):
        return self._md_file

    @property
    def model(self):
        return self._model

    @property
    def root_level(self):
        return self._root_level

    def write_title(self):
        self.md_file.new_header(level=self.root_level, title=self.model.id)

    def write_aliases(self):
        if not self.model.aliases:
            return
        self.md_file.new_line("Aliases:", bold_italics_code="i")
        bullet_points = MDList([alias for alias in self.model.aliases])
        self.md_file.new_line(bullet_points.get_md())

    def write_description(self):
        if not self.model.doc:
            return
        self.md_file.new_paragraph(self.model.doc)

    def write_fields(self):
        text = ["Field name", "Data type", "Required", "Description"] + [
            table_cell
            for field in self.model.fields
            for table_cell in [
                TextUtils.inline_code(field.id) if field.is_key else TextUtils.bold(field.id),
                field.type.type,
                MDSymbol.CHECK_MARK.value if field.is_required else " ",
                field.doc
            ]
        ]
        self.md_file.new_header(level=self.root_level+1, title="List of fields")
        self.md_file.new_table(
            4,
            len(self.model.fields) + 1,
            text
        )

    def write_nested_objects(self):
        # todo: implement this
        pass

    def write_references(self):
        self.md_file.new_header(level=self.root_level+1, title="External references")
        items = []
        if self.model.references:
            for reference in self.model.references:
                reference_name = (
                    reference.id_entity
                    if reference.name is None
                    else f"{TextUtils.bold(reference.name)} ({reference.id_entity})"
                )
                items.append(get_local_link(reference_name))
                items.append(
                    [
                        f"{mapping.source}: {mapping.destination}"
                        for mapping in reference.mapping
                    ]
                )
        self.md_file.new_paragraph(
            MDList(items).get_md()
        )


class MarkdownEntityWriter(MarkdownModelWriter):
    _model = Entity

    def __init__(self, md_file: MdUtils, model: Entity, root_level: int = 1):
        super().__init__(md_file, model, root_level)

    def write_referenced_by(self):
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
        md_file = MdUtils(
            file_name=self._config.output_path,
            title=self._data_model.name or self._data_model.id
        )
        if self._data_model.doc:
            md_file.new_paragraph(self._data_model.doc)
        self._write_entities(md_file)
        self._finalize(md_file)

    def _write_entities(self, md_file: MdUtils):
        entity_root_level = 1
        if self._data_model.shared_objects:
            md_file.new_header(level=1, title="Entities")
            entity_root_level = 2
        for entity in self._data_model.entities:
            entity_writer = MarkdownEntityWriter(md_file, entity, root_level=entity_root_level)
            entity_writer.write_title()
            entity_writer.write_aliases()
            entity_writer.write_description()
            entity_writer.write_fields()
            entity_writer.write_nested_objects()
            entity_writer.write_references()
            entity_writer.write_referenced_by()

    def _finalize(self, md_file: MdUtils):
        toc_depth = 1
        if self._data_model.shared_objects:
            toc_depth = 2
            self._write_shared_objects(md_file)
        md_file.new_table_of_contents(table_title='Index', depth=toc_depth)
        md_file.create_md_file()

    def _write_shared_objects(self, md_file: MdUtils):
        md_file.new_header(level=1, title="Shared objects")
        for obj in self._data_model.shared_objects:
            entity_writer = MarkdownModelWriter(md_file, obj, root_level=2)
            entity_writer.write_title()
            entity_writer.write_aliases()
            entity_writer.write_description()
            entity_writer.write_fields()
            entity_writer.write_nested_objects()
            entity_writer.write_references()


