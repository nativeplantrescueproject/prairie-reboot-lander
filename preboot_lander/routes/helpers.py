import time
from typing import List

from flask import (
    g,
    make_response,
    redirect,
    request,
)
from loguru import logger


def cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def log_before():
    g.start_time = time.perf_counter()


def log_after(response):
    total_time = time.perf_counter() - g.start_time
    time_ms = int(total_time * 1000)
    logger.info(f'Timing: {time_ms}ms [{request.method}] -> {request.path}')
    return response


def clear_trailing_slash():
    req_path = request.path
    if req_path != '/' and req_path.endswith('/'):
        return redirect(req_path[:-1])


def get_obj_attr_or_default(obj, attrs: List[str], default: str, layout: str = None):
    if obj is None:
        return default
    if layout is None:
        return ','.join([getattr(obj, attr) for attr in attrs])
    else:
        return layout.format(*[getattr(obj, attr) for attr in attrs])
