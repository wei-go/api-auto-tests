import logging
import allure
from module.base.base_request import Base
from configs.env_base_config import BaseConfig
from testdata.base.base_testdata import (
    TestData,
    TestDataUnitKeys
)


class Login(Base):
    def __init__(self, env_config: BaseConfig, test_data: TestData):
        super().__init__()
        self.env_config = env_config
        self.data = test_data

    def get_user_info(self) -> Base.ResponseObject:
        headers = {'Authorization': f'token {self.env_config.git_token}'}
        response = self.send_request(
            Base.RequestMethod.GET, headers=headers, custom_url=self.env_config.git_user_url)
        return response
