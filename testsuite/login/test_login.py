import pytest
from module.login.login import Login
from module.base.base_request import Base, BaseAssertion
from testdata.base.base_testdata import TestDataUnitKeys
from module.settings import Settings
from typing import Optional, Dict


@pytest.fixture(scope="module", autouse=True)
def _setup(setup: Settings):
    # Here is for spwning API controller instance
    setup.testsuite_controller = Login(
        setup.environment,
        setup.test_data
    )
    yield setup


@pytest.fixture(scope="function", autouse=True)
def params(setup: Settings):
    # Here is for API parameters or payloads
    params = setup.testsuite_controller.get_testdata_parameters(
        TestDataUnitKeys.parameters)
    yield params


@pytest.fixture(scope="function", autouse=True)
def expect_result(setup: Settings):
    # Here is for API expected results
    expect_result = setup.testsuite_controller.get_testdata_parameters(
        TestDataUnitKeys.expect)
    yield expect_result


class TestLogin:
    def test_git_user_info(self, setup: Settings, params, expect_result):
        actual_result = setup.testsuite_controller.get_user_info()
        TestLoginValidation.verify_user_info_is_successful(
            actual_result, expect_result)


class TestLoginValidation(BaseAssertion):
    @classmethod
    def verify_user_info_is_successful(cls, act: Base.ResponseObject, exp: Optional[Dict]):
        cls.verify_general_response_code(res=act)
        json_content = act.json
        assert json_content['login'] == exp['login'], "incorrect user name"
        assert json_content['id'] == exp['id'], "incorrect user id"
