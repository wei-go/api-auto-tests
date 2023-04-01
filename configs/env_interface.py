import abc
import os
from enum import Enum
from dataclasses import dataclass
from typing import TypedDict, List


class ENV_ENUMS(str, Enum):
    DEM = 'DEM'
    STG = 'STG'
    PRD = 'PRD'


@dataclass
class EnvironmentVariables:
    GIT_TOKEN = "GIT_TOKEN"


@dataclass
class ENV:
    GIT_DOMAIN: str
    GIT_TOKEN: str


@dataclass
class BaseConfig(abc.ABC):
    _https: str = 'https://'

    @property
    def git_url(self) -> str:
        return f'{self._https}{self.domain}'

    @property
    def git_user_url(self) -> str:
        return f'{self._https}{self.domain}/user'

    @property
    @abc.abstractmethod
    def domain(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def git_token(self) -> str:
        raise NotImplementedError
