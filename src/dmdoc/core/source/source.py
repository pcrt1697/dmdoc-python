import abc
import logging
from typing import Type

from pydantic import BaseModel

from dmdoc.core.sink.model import DataModel

_logger = logging.getLogger(__name__)


class BaseSource(abc.ABC):

    def __init__(self, config: BaseModel):
        self.config = config

    def process(self) -> DataModel:
        _logger.info("Started processing source [%s]", self.__class__.__name__)
        data_model = self._do_process()
        self.__validate(data_model)
        return data_model

    @abc.abstractmethod
    def _do_process(self) -> DataModel:
        pass

    @classmethod
    @abc.abstractmethod
    def get_config_class(cls) -> Type[BaseModel]:
        ...

    @classmethod
    def create(cls: Type["BaseSource"], config_dict: dict) -> "BaseSource":
        config = cls.get_config_class().parse_obj(config_dict)
        return cls(config=config)

    def __validate(self, data_model: DataModel):
        # todo: implement validation
        pass
