import logging

from dmdoc.core.formatter import Formatter
from dmdoc.core.sink.model import DataModel
from dmdoc.core.source import Source
from dmdoc.utils.file import is_yaml_file, read_yaml_with_envvars
from dmdoc.utils.importing import resolve_entrypoint_class

_logger = logging.getLogger(__name__)

_SOURCE_ENTRYPOINTS_PATH = "dmdoc.sources"
_FORMATS_ENTRYPOINTS_PATH = "dmdoc.formats"


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
    data_model = source.generate_data_model()
    formatter = load_formatter(formatter_filepath, data_model)
    formatter.generate()
