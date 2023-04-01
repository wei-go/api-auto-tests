from configs.env_interface import (
    BaseConfig,
    EnvironmentVariables,
    ENV_ENUMS,
    ENV
)
from dataclasses import dataclass
import os


@dataclass
class Base(BaseConfig):
    domain: str = ''
    git_token: str = ''

    def __init__(self, env: ENV):
        super().__init__()
        self.git_token = env.GIT_TOKEN
        self.domain = env.GIT_DOMAIN
