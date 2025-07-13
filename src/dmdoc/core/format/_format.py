import abc
import logging
from typing import Type

from pydantic import BaseModel

from dmdoc.core.sink.model import DataModel

_logger = logging.getLogger(__name__)


class Format(abc.ABC):

    def __init__(self, config: BaseModel, data_model: DataModel):
        self._config = config
        self._data_model = data_model

    def generate(self):
        """ Generate the documentation from sink DataModel. """

        _logger.info("Started output generation [%s]", self.__class__.__name__)
        self._before_generate()
        self._do_generate()

    def _before_generate(self):
        """ Executed before precessing. Override if needed, e.g. to apply some validation. """
        pass

    @abc.abstractmethod
    def _do_generate(self):
        """ Actual implementation to generate the documentation. """
        pass

    @classmethod
    @abc.abstractmethod
    def get_config_class(cls) -> Type[BaseModel]:
        """ Returns the configuration class used by this format. """
        ...

    @classmethod
    def create(cls: Type["Format"], data_model: DataModel, config_dict: dict) -> "Format":
        """ Utility method to create a new instance. """

        config_cls = cls.get_config_class()
        if config_cls is None:
            config = None
        else:
            config = cls.get_config_class().model_validate(config_dict)
        return cls(config=config, data_model=data_model)
