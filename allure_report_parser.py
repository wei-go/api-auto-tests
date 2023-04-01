import os
import gspread
import logging
from retry import retry
from argparse import ArgumentParser
from module.file_operation import read_json
from typing import List, Optional, Dict, Any
from arrow.arrow import Arrow
from conftest import (
    TestsuiteConfig,
    load_testsuite_config
)
from dataclasses import (
    dataclass,
    field
)


GCLOUD_CRED = os.environ.get('GCLOUD_AUTH_PATH')
SPREADSHEET_ID = os.environ.get('SHEET_ID')
ROW_DATA_WORKSHEET = 'test_result_raw'


@dataclass
class TestResultObject:
    name: str = None
    status: str = None
    start_time: int = None
    end_time: int = 0
    duration: int = 0
    uuid: str = None
    testcase_id: str = None
    full_testcase_name: str = None
    severity: str = None
    tags: List[str] = field(default_factory=list)
    parent_suite: str = None
    suite: str = None
    subsuite: str = None
    host: str = None
    framework: str = None
    package: str = None
    execution_time: int = 0


@dataclass
class GoogleSheetManager(object):
    # If modifying these scopes, delete the file token.json.
    _SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
               'https://www.googleapis.com/auth/drive.file',
               'https://www.googleapis.com/auth/drive']
    _sheet: gspread.Spreadsheet = None
    _spreadsheet_id: str = ''
    _current_ts = Arrow.now().int_timestamp

    def __init__(self, auth_path: str, spreadsheet_id: str) -> None:
        self._spreadsheet_id = spreadsheet_id
        gc = gspread.service_account(filename=auth_path, scopes=self._SCOPES)
        self._sheet = gc.open_by_key(spreadsheet_id)

        pass

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def insert_test_result_rows(self, record_objs: List[TestResultObject]):
        worksheet_name = 'test_result_raw'
        range = 'A:L'
        test_results_sht = self._sheet.worksheet(worksheet_name)
        # cols: [tc_id	tc_name	package	filename	class	status	start_time	end_time	duration	execution_time	severity	host]
        rows = []
        for obj in record_objs:
            row = [
                obj.testcase_id,
                obj.name,
                obj.package,
                obj.suite,
                obj.subsuite,
                obj.status,
                obj.start_time,
                obj.end_time,
                obj.duration,
                obj.execution_time,
                obj.severity,
                obj.host
            ]
            rows.append(row)

        response = test_results_sht.append_rows(
            values=rows,
            table_range=range
        )

        print(response)
        pass

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def insert_tc_tag(self, record_obj: TestResultObject):
        worksheet_name = 'testcase_with_tags'
        work_sheet = self._sheet.worksheet(worksheet_name)
        # testcase_id	package	testcase_name	tag	updated_ts
        rows = []
        for tag in record_obj.tags:
            row = [
                record_obj.testcase_id,
                record_obj.package,
                record_obj.name,
                tag,
                self._current_ts
            ]
            rows.append(row)

        response = work_sheet.append_rows(
            values=rows
        )
        print(response)
        pass

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def update_severity(self, record_obj: TestResultObject):
        worksheet_name = 'testcase_with_severity'
        work_sheet = self._sheet.worksheet(worksheet_name)
        # testcase_id	package	testcase_name	severity	updated_ts
        cell: gspread.cell.Cell = work_sheet.find(
            record_obj.testcase_id, in_column=1)

        if cell:
            if work_sheet.cell(cell.row, 4).value != record_obj.severity:
                work_sheet.update_cell(cell.row, 4, record_obj.severity)
                work_sheet.update_cell(cell.row, 5, self._current_ts)
        else:
            # Append New Row for Severity
            work_sheet.append_row(
                [
                    record_obj.testcase_id,
                    record_obj.package,
                    record_obj.name,
                    record_obj.severity,
                    self._current_ts
                ]
            )
        pass

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def find_rows_by_value(self, sheet_name: str, value: Any = None) -> List[gspread.Cell]:
        work_sheet = self._sheet.worksheet(sheet_name)
        cell_list = work_sheet.findall(value)
        return cell_list

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def delete_row_by_index(self, sheet_name: str, row_index: int):
        work_sheet = self._sheet.worksheet(sheet_name)
        work_sheet.delete_row(row_index)

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def insert_suite_execution_status(self, record_objs: List[TestResultObject]):
        worksheet_name = 'suite_execution_status'
        work_sheet = self._sheet.worksheet(worksheet_name)
        class_name = ''
        num_pass = 0
        num_fail = 0
        num_break = 0
        num_skip = 0
        num_unknown = 0
        num_count = 0
        for obj in record_objs:
            class_name = obj.subsuite
            num_count += 1
            if obj.status == 'passed':
                num_pass += 1
            elif obj.status == 'broken':
                num_break += 1
            elif obj.status == 'skipped':
                num_skip += 1
            elif obj.status == 'unknown':
                num_unknown += 1

        response = work_sheet.append_row(
            values=[
                class_name,
                num_pass,
                num_fail,
                num_break,
                num_skip,
                num_unknown,
                num_count,
                self._current_ts
            ]
        )
        print(response)

    @retry(exceptions=gspread.exceptions.APIError, tries=60, delay=2, max_delay=60, backoff=2, jitter=0, logger=logging)
    def insert_war_map(self, config: TestsuiteConfig, result_objs: List[TestResultObject]):
        worksheet_name = 'coverage_map'
        work_sheet = self._sheet.worksheet(worksheet_name)

        passed_count = 0
        failed_count = 0

        for obj in result_objs:
            if obj.status == "passed":
                passed_count += 1
            else:
                failed_count += 1

        row = [
            config.metadata.testsuite,
            config.metadata.city_name,
            config.metadata.city_id,
            passed_count,
            failed_count,
            passed_count + failed_count,
            self._current_ts
        ]
        work_sheet.append_row(row)


def get_arguments() -> Optional[Dict]:
    parser = ArgumentParser()
    parser.add_argument("--report_path", dest='report_path', action='store',
                        help='set report path', default="report/allure")
    parser.add_argument("--testsuite_config", dest='testsuite_config', action='store',
                        help='testsuite_config', default=None)
    args_obj = parser.parse_args()
    args = {
        'report_path': args_obj.report_path,
        'testsuite_config': args_obj.testsuite_config
    }
    return args


def get_result_files(_report_path: str) -> List[str]:
    files = []
    root_path = f'{os.path.dirname(os.path.realpath(__file__))}/{_report_path}'
    for file in os.listdir(root_path):
        if file.endswith('result.json'):
            files.append(os.path.join(root_path, file))
    return files


def get_testcase_result(filepath: str) -> TestResultObject:
    result_json = read_json(filepath)
    result = TestResultObject()
    result.name = result_json['name']
    result.status = result_json['status']
    result.start_time = result_json['start']
    result.end_time = result_json['stop']
    result.duration = result_json['stop'] - result_json['start']
    result.uuid = result_json['uuid']
    result.testcase_id = result_json['testCaseId']
    result.full_testcase_name = result_json['fullName']
    result.execution_time = Arrow.now().int_timestamp * 1000
    for label in result_json['labels']:
        k, v = label['name'], label['value']
        if k == 'severity':
            result.severity = v
            continue
        if k == 'tag':
            result.tags.append(v)
            continue
        if k == 'parentSuite':
            result.parent_suite = v
            continue
        if k == 'parentSuite':
            result.parent_suite = v
            continue
        if k == 'suite':
            result.suite = v
            continue
        if k == 'suite':
            result.suite = v
            continue
        if k == 'subSuite':
            result.subsuite = v
            continue
        if k == 'host':
            result.host = v
            continue
        if k == 'package':
            result.package = v
            continue
    return result


if __name__ == "__main__":
    args = get_arguments()
    files = get_result_files(args['report_path'])
    testsuite_config = load_testsuite_config(args['testsuite_config'])

    sheet_manager = GoogleSheetManager(
        auth_path=GCLOUD_CRED,
        spreadsheet_id=SPREADSHEET_ID
    )
    test_results: List[TestResultObject] = []
    for f in files:
        test_results.append(get_testcase_result(f))

    # Update Record
    sheet_manager.insert_test_result_rows(test_results)
    # Append Suite Execution Status
    sheet_manager.insert_suite_execution_status(test_results)
    # Insert Tags
    for test_obj in test_results:
        # Append New Tag
        sheet_manager.insert_tc_tag(test_obj)
        # Update Severity
        sheet_manager.update_severity(test_obj)

    # Update Coverage Map
    sheet_manager.insert_war_map(testsuite_config, test_results)

    pass
