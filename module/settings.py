# flake8: noqa: E501
import logging
import os
from enum import Enum
from dataclasses import dataclass
from importlib import import_module
import requests
from module.file_operation import (
    read_yml,
    read_json
)
from configs.env_stg import STG
from configs.env_base_config import Base as BaseConfig
from configs.env_interface import ENV_ENUMS
from testdata.base.base_testdata import TestData
from module.base.base_request import Base
from typing import TypedDict, List


class TestsuiteSettings:
    def __init__(self):
        self.console_url = ""
        self.console_payload = None
        self.query_url = ""
        self.auth = ""
        self.header = None
        self.payload = None


@ dataclass
class Settings:
    environment: BaseConfig = None
    testsuite_controller: Base = None
    test_data: TestData = None

    # ----------------------------------------------------------------------------#
    # initialize logging when doing test base setup
    # ----------------------------------------------------------------------------#
    def __init__(self, request) -> None:
        # get custom config from command line args
        args = {
            'env': request.config.getoption('--env', default="STG"),
            'test_data': request.config.getoption('--test_data', default=None),
            'testsuite_config': request.config.getoption("--testsuite_config", default="")
        }
        logging.info('input args: %s', args)
        self.environment = self.set_env(args['env'])
        self.headers = {}
        self.test_data = self.get_testdata(args["test_data"])(
            env_config=self.environment
        )

    def set_env(self, env: str = "STG") -> BaseConfig:
        _env = {
            ENV_ENUMS.STG.value: STG
        }
        return BaseConfig(_env[env])

    def get_testdata(self, path: str) -> TestData:
        return import_module(f'testdata.{path}/testdata'.replace("/", "."), f'{path}/testdata.py').TestData
