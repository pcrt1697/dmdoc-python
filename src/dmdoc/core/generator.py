import logging
from importlib.metadata import entry_points
from typing import TypeVar

from dmdoc.core.formatter import Formatter
from dmdoc.core.sink.model import DataModel
from dmdoc.core.source import Source
from dmdoc.utils.file import is_yaml_file, read_yaml_with_envvars
from dmdoc.utils.importing import import_object

_logger = logging.getLogger(__name__)

_SOURCE_ENTRYPOINTS_PATH = "dmdoc.sources"
_FORMATS_ENTRYPOINTS_PATH = "dmdoc.formats"


_T = TypeVar("_T")


def resolve_entrypoint_class(name: str, group: str, parent_class: type[_T]) -> type[_T]:
    entrypoints = entry_points(name=name, group=group)
    try:
        entrypoint = entrypoints[name]
    except Exception as e:
        raise ValueError(f"Cannot find entrypoint named `{name}` belonging to group `{group}`") from e
    try:
        _class = import_object(entrypoint.value)
    except ImportError as ie:
        raise ValueError(
            f"Failed to import entrypoint class with name `{name}`: maybe an optional dependency is not installed"
        ) from ie
    except Exception as e:
        raise ValueError(f"Failed to import entrypoint class with key `{name}`") from e
    if not issubclass(_class, parent_class):
        raise ValueError(f"Invalid entrypoint class for key `{name}` {_class}: it must inherit from {parent_class}")
    return _class


def load_source(source_filepath: str) -> Source:
    if not is_yaml_file(source_filepath):
        raise ValueError(f"Source filepath is not a YAML file [{source_filepath}]")
    source_dict = read_yaml_with_envvars(source_filepath)
    source_type = source_dict.get("type")
    if source_type is None:
        raise ValueError(f"Missing required source type identifier `type` [{source_filepath}]")
    _logger.info(f"Loading source class for type `{source_type}`")
    source_class: type[Source] = resolve_entrypoint_class(
        name=source_type,
        group=_SOURCE_ENTRYPOINTS_PATH,
        parent_class=Source
    )
    config = source_dict.get("config")
    return source_class.create(config_dict=config)


def load_formatter(formatter_filepath: str, data_model: DataModel) -> Formatter:
    if not is_yaml_file(formatter_filepath):
        raise ValueError(f"Formatter filepath is not a YAML file [{formatter_filepath}]")
    formatter_dict = read_yaml_with_envvars(formatter_filepath)
    format_type = formatter_dict.get("format")
    if format_type is None:
        raise ValueError(f"Missing required format type identifier `format` [{formatter_filepath}]")
    _logger.info(f"Loading formatter class for type `{format_type}`")
    formatter_class: type[Formatter] = resolve_entrypoint_class(
        name=format_type,
        group=_FORMATS_ENTRYPOINTS_PATH,
        parent_class=Formatter
    )
    config = formatter_dict.get("config")
    return formatter_class.create(
        data_model=data_model,
        config_dict=config
    )


def generate_documentation(source_filepath: str, formatter_filepath: str):
    if not is_yaml_file(source_filepath):
        raise ValueError(f"Source filepath is not a YAML file [{source_filepath}]")
    if not is_yaml_file(formatter_filepath):
        raise ValueError(f"Formatter filepath is not a YAML file [{formatter_filepath}]")
    source = load_source(source_filepath)
    data_model = source.process()
    formatter = load_formatter(formatter_filepath, data_model)
    formatter.generate()
