import logging
import sys

from flask import (
    Flask,
    jsonify,
    request,
)
from loguru import logger
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from preboot_lander.config import DevelopmentConfig
from preboot_lander.routes.helpers import (
    clear_trailing_slash,
    log_after,
    log_before,
)
from preboot_lander.routes.main import bp_main

ROUTES = [
    bp_main,
]


class InterceptHandler(logging.Handler):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger

    def emit(self, record):
        # Get corresponding loguru level if it exists
        try:
            level = self.logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find call whence the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        self.logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def handle_err(err):
    logger.error(err)
    if err.code == 404:
        logger.error(f'Path requested: {request.path}')

    if isinstance(err, HTTPException):
        err_msg = getattr(err, 'description', HTTP_STATUS_CODES.get(err.code, ''))
        return jsonify({'message': err_msg}), err.code
    if not getattr(err, 'message', None):
        return jsonify({'message': 'Server has encountered an error.'}), 500
    return jsonify(**err.kwargs), err.http_status_code


def handle_exception(exc_type, exc_value, exc_traceback):
    """This is used to patch over sys.excepthook so uncaught logs are also recorded"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # We'll log uncaught errors as critical to differentiate them from caught `error` level entries
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical('Uncaught exception:')


def configure_log(app):
    BASE_FORMAT = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | ' \
                  '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
    sys.excepthook = handle_exception
    handlers = [
        {
            'sink': sys.stdout,
            'level': app.config.get('LOG_LEVEL'),
            'format': BASE_FORMAT,
            'backtrace': app.config.get('DEBUG')
        }
    ]

    if app.config.get('LOG_DIR') is not None:
        # Add a filepath to the handlers list
        # First, ensure all the directories are made
        app.config.get('LOG_DIR').mkdir(parents=True, exist_ok=True)
        handlers.append({
            'sink': app.config.get('LOG_DIR').joinpath('scraper-webapp.log'),
            'level': app.config.get('LOG_LEVEL'),
            'rotation': '7 days',
            'retention': '30 days',
            'format': BASE_FORMAT,
            'enqueue': True,
            'backtrace': app.config.get('DEBUG')
        })
    config = {
        'handlers': handlers,
    }
    logger.configure(**config)


def create_app(*args, **kwargs) -> Flask:
    """Creates a Flask app instance"""
    # Config app, default to development if not provided
    config_class = kwargs.pop('config_class', DevelopmentConfig)

    app = Flask(__name__, static_url_path='/')
    app.config.from_object(config_class)
    # Reduce the amount of 404s by disabling strict slashes (e.g., when a forward slash is appended to a url)
    app.url_map.strict_slashes = False

    # Initialize logger
    configure_log(app=app)

    # logger = get_logger(app.config.get('NAME'), log_dir_path=app.config.get('LOG_DIR'),
    #                     show_backtrace=app.config.get('DEBUG'), base_level=app.config.get('LOG_LEVEL'))
    logger.info('Logger started. Binding to app handler...')
    app.logger.addHandler(InterceptHandler(logger=logger))
    # Bind logger so it's easy to call from app object in routes
    app.extensions.setdefault('logg', logger)

    # Register routes
    logger.info('Registering routes...')
    for ruut in ROUTES:
        app.register_blueprint(ruut)

    for err_code, name in HTTP_STATUS_CODES.items():
        if err_code >= 400:
            try:
                app.register_error_handler(err_code, handle_err)
            except ValueError:
                pass

    app.before_request(log_before)
    app.before_request(clear_trailing_slash)
    # app.before_request(handle_preflight)
    app.after_request(log_after)
    # app.after_request(set_headers)

    return app
