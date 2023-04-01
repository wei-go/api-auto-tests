# flake8: noqa E501
import logging
import json
import os
import uuid
import gzip
import requests
from enum import Enum
from requests.models import Response
from testdata.base.base_testdata import (
    TestData,
    TestDataUnitKeys
)
logger = logging.getLogger(__name__)


class Base(object):
    data: TestData

    class ResponseObject(object):
        def __init__(self, response: Response):
            self.status_code = response.status_code
            self.content = response.content
            self.text = response.text
            try:
                self.json = response.json()
            except Exception as e:
                self.json = None
                logger.warning(e)
            self.header = response.headers
            self.url = response.url

    class RequestMethod(str, Enum):
        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"

    def __init__(self) -> None:
        pass

    def send_request(self,
                     method: RequestMethod = RequestMethod.GET,
                     payload=None,
                     chunk_size: int = 0,
                     cookies=None,
                     custom_url: str = None,
                     headers=None,
                     files: list = None
                     ) -> ResponseObject:

        _payload = None

        if files:
            _payload = {}

        if custom_url is None:
            logging.error("should provide url when sending request")

        if method in (self.RequestMethod.POST, self.RequestMethod.PUT, self.RequestMethod.PATCH) and (payload is None and not files):
            logging.error(
                "should provide payload of files when sending request")
        else:
            _payload = payload

        if headers is None:
            _headers = {"Content-Type": "application/json"}
        else:
            _headers = headers

        # new request session
        res = None
        if res is None:
            session_res = requests.session()

        if method is self.RequestMethod.GET:
            res = session_res.get(
                custom_url, headers=_headers, cookies=cookies, stream=True)
        elif method is self.RequestMethod.POST:
            res = session_res.post(
                custom_url, headers=_headers, cookies=cookies, stream=True, json=_payload, files=files)
        elif method is self.RequestMethod.PUT:
            res = session_res.put(custom_url, headers=_headers,
                                  cookies=cookies, stream=True, json=_payload, files=files)
        elif method is self.RequestMethod.DELETE:
            res = session_res.delete(
                custom_url, headers=_headers, cookies=cookies, stream=True)
        elif method is self.RequestMethod.PATCH:
            res = session_res.patch(
                custom_url, headers=_headers, cookies=cookies, stream=True, json=_payload, files=files)
        else:
            res = session_res.put(custom_url, headers=_headers,
                                  cookies=cookies, stream=True, data=_payload, files=files)

        res_obj = self.ResponseObject(res)

        # TODO
        logger.info("\n=============URL=================\n")
        logger.info(res_obj.url)
        logger.info("\n============Payload==============\n")
        logger.info(payload)
        logger.info("\n============Response=============\n")
        if len(res.content) < 10000:
            logger.info(f'status code: {res}\n{res_obj.text}')
        else:
            logger.info("Too large response body, skipped to print.")
        logger.info("\n=================================\n")

        if res.status_code == 202:
            logger.warning(
                "\n==============Source Not Ready===================\n")
            logger.warning(
                "return code is 202, source are not ready. please check source status.")

        return res_obj

    def json_to_gzip(self, data):
        bytes_data = bytes(json.dumps(data), encoding='utf-8')
        gz_data = gzip.compress(bytes_data, 5)
        return gz_data

    def get_specific_parameters(self, testcase_key: str, param_key: TestDataUnitKeys):
        return self.data.data[TestDataUnitKeys.content][testcase_key][param_key]

    def get_testdata_parameters(self, key: TestDataUnitKeys):
        testcase_name = os.environ.get(
            'PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        if testcase_name in self.data.data[TestDataUnitKeys.content].keys():
            return self.data.data[TestDataUnitKeys.content][testcase_name][key]
        else:
            logger.info(f'not found key in test data: {testcase_name}')
            return {}


class BaseAssertion:
    @classmethod
    def log_assert(cls, func, messages):
        if not func:
            logging.error(messages)
        assert func, messages

    @classmethod
    def verify_general_error_in_qgl_response(cls, res: Base.ResponseObject):
        '''
        :param res: a Response object via graphQL result
        :return:
        [Check Points]
        1. Status Code should be 200
        2. Content should be Json format
        3. Have data key in Json
        4. Not found Error key in Json
        '''
        BaseAssertion.verify_general_response_code(res)
        assert res.json is not None, "Assertion Failure, Response body is not Json."
        data = res.json
        cls.log_assert("errors" not in data, "get qgl error response. errors: {}".format(
            data
        ))

    @classmethod
    def verify_response_code(cls, res: Base.ResponseObject, expected_status_code: int):
        cls.log_assert(res.status_code == expected_status_code,
                       "Assertion Failure, The status code is not {}, status: {}, body: {}".format(expected_status_code, res.status_code, res.text))

    @classmethod
    def verify_general_response_code(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 200)

    @classmethod
    def verify_response_code_with_201(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 201)

    @classmethod
    def verify_response_code_with_202(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 202)

    @classmethod
    def verify_response_code_with_204(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 204)

    @classmethod
    def verify_general_forbidden_response_code(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 403)

    @classmethod
    def verify_response_code_with_404(cls, res: Base.ResponseObject):
        cls.verify_response_code(res, 404)

    @classmethod
    def verify_general_bad_request(cls, res: Base.ResponseObject):
        # Valid Result Example
        # {
        #     "error_code": 40001,
        #     "error_message": "bad request"
        # }
        if res.status_code == 400:
            cls.log_assert(res.json is not None,
                           "Assertion Failure, Response body is not Json.")
            # assert res.json.__contains__("error_code"), "Assertion Failure, No error_code key."
            # assert res.json.__contains__("error_message"), "Assertion Failure, No error_message key."
            #
            # assert res.json["error_code"] == 40001, \
            #     "Assertion Failure, Incorrect error_code: {}".format(res.json["error_code"])
            # assert res.json["error_message"] == "bad request", \
            #     "Assertion Failure, Incorrect error message: {}".format(res.json["error_message"])
        else:
            cls.log_assert(
                False, "Assertion Failure, The status code is not 400, body: {}".format(res.text))

    @classmethod
    def verify_general_bad_request_with_403(cls, res: Base.ResponseObject):
        # Valid Result Example
        # {
        #     "error_code": 40301,
        #     "error_message": "forbidden error"
        # }
        if res.status_code == 403:
            cls.log_assert(res.json is not None,
                           "Assertion Failure, Response body is not Json.")
            cls.log_assert(res.json.__contains__("error_code"),
                           "Assertion Failure, No error_code key.")
            cls.log_assert(res.json.__contains__("error_message"),
                           "Assertion Failure, No error_message key.")

            cls.log_assert(res.json["error_code"] == 40301,
                           "Assertion Failure, Incorrect error_code: {}".format(res.json["error_code"]))
            cls.log_assert(res.json["error_message"] == "forbidden error",
                           "Assertion Failure, Incorrect error message: {}".format(res.json["error_message"]))
        else:
            cls.log_assert(
                False, "Assertion Failure, The status code is not 403, body: {}".format(res.text))

    @classmethod
    def verify_general_bad_request_with_405(cls, res: Base.ResponseObject):
        # Valid Result Example
        # {
        #     "error_code": 40005,
        #     "error_message": "bad request"
        # }
        if res.status_code == 400:
            cls.log_assert(res.json is not None,
                           "Assertion Failure, Response body is not Json.")
            cls.log_assert(res.json.__contains__("error_code"),
                           "Assertion Failure, No error_code key.")
            cls.log_assert(res.json.__contains__("error_message"),
                           "Assertion Failure, No error_message key.")

            cls.log_assert(res.json["error_code"] == 40005,
                           "Assertion Failure, Incorrect error_code: {}".format(res.json["error_code"]))
            cls.log_assert(res.json["error_message"] == "bad request",
                           "Assertion Failure, Incorrect error message: {}".format(res.json["error_message"]))
        else:
            cls.log_assert(
                False, "Assertion Failure, The status code is not 405, body: {}".format(res.text))

    @classmethod
    def verify_general_resource_error(cls, res: Base.ResponseObject):
        # Valid Result Example
        # {
        #     "error_code": 40900,
        #     "error_message": "resource error"
        # }
        if res.status_code == 409:
            cls.log_assert(res.json is not None,
                           "Assertion Failure, Response body is not Json.")
            cls.log_assert(res.json.__contains__("error_code"),
                           "Assertion Failure, No error_code key.")
            cls.log_assert(res.json.__contains__("error_message"),
                           "Assertion Failure, No error_message key.")

            cls.log_assert(res.json["error_code"] == 40900,
                           "Assertion Failure, Incorrect error_code: {}".format(res.json["error_code"]))
            cls.log_assert(res.json["error_message"] == "resource error",
                           "Assertion Failure, Incorrect error message: {}".format(res.json["error_message"]))
        else:
            cls.log_assert(
                False, "Assertion Failure, The status code is not 409, body: {}".format(res.text))

    @classmethod
    def verify_bad_formula_error(cls, res: Base.ResponseObject):
        # Valid Result Example
        # {
        #     "error_code": 40006,
        #     "error_message": "bad formula"
        # }
        if res.status_code == 400:
            cls.log_assert(res.json is not None,
                           "Assertion Failure, Response body is not Json.")
            cls.log_assert(res.json.__contains__("error_code"),
                           "Assertion Failure, No error_code key.")
            cls.log_assert(res.json.__contains__("error_message"),
                           "Assertion Failure, No error_message key.")

            cls.log_assert(res.json["error_code"] == 40006,
                           "Assertion Failure, Incorrect error_code: {}".format(res.json["error_code"]))
            cls.log_assert(res.json["error_message"] == "bad formula",
                           "Assertion Failure, Incorrect error message: {}".format(res.json["error_message"]))
        else:
            cls.log_assert(
                False, "Assertion Failure, The status code is not 40006, body: {}".format(res.text))

    @classmethod
    def verify_expected_return_info(cls, res: Base.ResponseObject, exp_code: int, exp_msg: str = None):
        cls.log_assert(res.status_code == exp_code,
                       "Assertion Failure, return code is not expected. act: {}, msg: {}, exp: {}".format(
                           res.status_code,
                           res.text,
                           exp_code
                       ))
        if exp_msg:
            cls.log_assert(res.json["message"] == exp_msg,
                           "Assertion Failure, return messages is not expected. act: {}, exp: {}".format(
                res.text,
                exp_msg
            ))
