import abc
import logging
from typing import Type

from pydantic import BaseModel

from dmdoc.core.sink.model import DataModel

_logger = logging.getLogger(__name__)


class Source(abc.ABC):

    def __init__(self, config: BaseModel):
        self._config = config

    def parse(self) -> DataModel:
        """ Parse the source data model to sink DataModel. """

        _logger.info("Started processing source [%s]", self.__class__.__name__)
        self._before_parse()
        data_model = self._do_parse()
        return data_model

    def _before_parse(self):
        """ Executed before precessing. Override if needed, e.g. to apply some validation. """
        pass

    @abc.abstractmethod
    def _do_parse(self) -> DataModel:
        """ Actual implementation to produce the data model. """
        ...

    @classmethod
    @abc.abstractmethod
    def get_config_class(cls) -> Type[BaseModel]:
        """ Returns the configuration class used by this source. """
        ...

    @classmethod
    def create(cls: Type["Source"], config_dict: dict) -> "Source":
        """ Utility method to create a new instance. """

        config_cls = cls.get_config_class()
        if config_cls is None:
            config = None
        else:
            config = cls.get_config_class().model_validate(config_dict)
        return cls(config=config)
