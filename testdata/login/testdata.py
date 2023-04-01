from configs.env_interface import BaseConfig
from testdata.base.base_testdata import (
    TestDataObject,
    TestDataUnitObject,
    BaseTestData
)
from dataclasses import dataclass


@dataclass
class TestData(BaseTestData):
    data: TestDataObject = None
    config: BaseConfig = None

    def __init__(self, env_config: BaseConfig) -> None:
        super().__init__()
        self.config = env_config
        self.data = TestDataObject(
            content={
                'test_git_user_info': TestDataUnitObject(
                    parameters={
                        # Request Payload here
                    },
                    expect={
                        "login": "GIT_USER_NAME",
                        "id": 0000
                    }
                )
            }
        )
