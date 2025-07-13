import logging

from dmdoc.core.format import Format
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


def load_format(format_filepath: str, data_model: DataModel) -> Format:
    if not is_yaml_file(format_filepath):
        raise ValueError(f"Format filepath is not a YAML file [{format_filepath}]")
    format_dict = read_yaml_with_envvars(format_filepath)
    format_type = format_dict.get("format")
    if format_type is None:
        raise ValueError(f"Missing required format type identifier `format` [{format_filepath}]")
    _logger.info(f"Loading format class for type `{format_type}`")
    format_class: type[Format] = resolve_entrypoint_class(
        name=format_type,
        group=_FORMATS_ENTRYPOINTS_PATH,
        parent_class=Format
    )
    config = format_dict.get("config")
    return format_class.create(
        data_model=data_model,
        config_dict=config
    )


def generate_documentation(source_filepath: str, format_filepath: str):
    if not is_yaml_file(source_filepath):
        raise ValueError(f"Source filepath is not a YAML file [{source_filepath}]")
    if not is_yaml_file(format_filepath):
        raise ValueError(f"Format filepath is not a YAML file [{format_filepath}]")
    source = load_source(source_filepath)
    data_model = source.parse()
    format_ = load_format(format_filepath, data_model)
    format_.generate()
