from dataclasses import dataclass
from module.file_operation import read_json
from module.settings import Settings
from datetime import datetime
from typing import List
import allure
import json
import pytest


@dataclass
class TestsuiteConfig:
    @dataclass
    class metadata_obj:
        testsuite: str
        tags: list
        city_name: str
        city_id: int

    @dataclass
    class testcase_obj:
        name: str = None
        tags: List[str] = list
        severity: str = None
        story: str = None
        feature: str = None
        testrail_suite_id: int = 0
        testrail_case_id: int = 0

    metadata: metadata_obj = None
    testcases: List[testcase_obj] = list


def load_testsuite_config(path: str) -> TestsuiteConfig:
    config_json = read_json(path)

    config = TestsuiteConfig(
        metadata=None,
        testcases=[]
    )

    config.metadata = TestsuiteConfig.metadata_obj(
        testsuite=config_json['metadata']['testsuite_name'],
        tags=config_json['metadata']['tags'],
        city_name=config_json['metadata']['city_name'],
        city_id=config_json['metadata']['city_id']
    )

    for item in config_json['testcases']:
        tc = TestsuiteConfig.testcase_obj(
            name=item['name'],
            tags=item['tags'],
            severity=item['severity'],
            story=item['story'],
            feature=item['feature'],
            testrail_suite_id=item['testrail_suite_id'],
            testrail_case_id=item['testrail_case_id']
        )
        config.testcases.append(tc)

    return config


def pytest_addoption(parser):
    parser.addoption('--env', action='store',
                     help='setup environment; STAGING, PROD', default="STG")
    parser.addoption('--test_data', action='store',
                     help='setup name of test data set (ex: test_data_set_1)')
    parser.addoption('--testsuite_config', action='store',
                     help='path of testsuite config')


def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line("markers",
                            "version(number): mark test to run only on named version")


@pytest.fixture(scope="session", autouse=True)
def setup(request: Settings):
    setup = Settings(request)
    yield setup


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(session, config, items):
    testsuite_config_path = config.getoption("--testsuite_config", default="")
    testsuite_config: TestsuiteConfig = load_testsuite_config(
        testsuite_config_path)
    testcase_obj: TestsuiteConfig.testcase_obj = None

    for item in session.items:
        testcase_name = item.name
        for tc in testsuite_config.testcases:
            if tc.name == testcase_name:
                testcase_obj = tc
                break

        if testcase_obj:
            # Add Marker for Testcase
            if testcase_obj.severity:
                item.add_marker(allure.severity(testcase_obj.severity))
                item.add_marker(allure.tag(*testcase_obj.tags))
                item.add_marker(allure.story(*testcase_obj.story))
                item.add_marker(allure.feature(*testcase_obj.feature))
            testcase_obj = None

        print(testcase_obj)
    pass
