import abc
import logging
from typing import Type

from pydantic import BaseModel

from dmdoc.core.sink.model import DataModel

_logger = logging.getLogger(__name__)


class Source(abc.ABC):

    def __init__(self, config: BaseModel):
        self._config = config

    def generate_data_model(self) -> DataModel:
        """ Generate the data model. """
        _logger.info("Started processing source [%s]", self.__class__.__name__)
        self._before_generate()
        data_model = self._do_generate()
        self.__validate(data_model)
        return data_model

    def _before_generate(self):
        """ Executed before precessing. Override if needed, e.g. to apply some validation. """
        pass

    @abc.abstractmethod
    def _do_generate(self) -> DataModel:
        """ Actual implementation to produce the data model. """
        ...

    @classmethod
    @abc.abstractmethod
    def get_config_class(cls) -> Type[BaseModel]:
        """ Actual implementation to produce the data model. """
        ...

    @classmethod
    def create(cls: Type["Source"], config_dict: dict) -> "Source":
        config_cls = cls.get_config_class()
        if config_cls is None:
            config = None
        else:
            config = cls.get_config_class().model_validate(config_dict)
        return cls(config=config)

    def __validate(self, data_model: DataModel):
        # todo: implement validation
        pass
