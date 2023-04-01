import logging
import time
from typing import Callable
from module.base.base_request import Base

logger = logging.getLogger(__name__)


def polling_response(
        request_func: Callable, request_func_args: tuple, response_condition_func: Callable,
        retries_limit: int = 30, step: int = 10) -> Base.ResponseObject:
    """Polling the response from request_fuc and try to meet the matching condition.
    If the condition is not met, try again until retries limit reached.
    Args:
        request_func: request function (eg. requests.get)
        request_func_args: request function arguments in tuple (eg. ('http://google.com', ))
        response_condition_func: assert method for request_func(*request_func_args) - True or False
        retries: retries limit, default 30
        step: sleep time between retries in seconds, default 10
    """
    response = None
    retries = 0
    while retries < retries_limit:
        response = request_func(*request_func_args)
        if response_condition_func(response):
            logger.info(f'condition success! after {retries} retries')
            break
        time.sleep(step)
        retries += 1
        logger.info(
            f'waiting for target condition {response_condition_func.__name__} met ...'
            f'{retries}/{retries_limit}'
        )
    return response
