import os
from configs.env_interface import (
    ENV,
    EnvironmentVariables
)
from dataclasses import dataclass


@dataclass
class STG(ENV):
    GIT_DOMAIN = "api.github.com"
    GIT_TOKEN = os.getenv(EnvironmentVariables.GIT_TOKEN)
