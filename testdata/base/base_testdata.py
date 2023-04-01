import abc
from dataclasses import dataclass
from typing import (
    Optional,
    TypedDict,
    Dict
)
from configs.env_interface import (
    BaseConfig
)


class TestDataUnitKeys:
    parameters = 'parameters'
    expect = 'expect'
    addtional = 'addtional'
    content = 'content'


class TestDataUnitObject(TypedDict):
    parameters: Optional[Dict]
    expect: Optional[Dict]
    addtional: Optional[Dict]


class TestDataObject(TypedDict):
    content: Dict[str, TestDataUnitObject]


@dataclass
class BaseTestData(abc.ABC):

    @abc.abstractmethod
    def __init__(self) -> None:
        super().__init__()

    @property
    @abc.abstractmethod
    def data(self) -> TestDataObject:
        raise NotImplementedError


@dataclass
class TestData(BaseTestData):
    data: TestDataObject = None
    config: BaseConfig = None

    def __init__(self, env_config: BaseConfig) -> None:
        super().__init__()
