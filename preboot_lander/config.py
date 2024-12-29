"""Configuration setup"""
from importlib import metadata
import os

from loguru import logger


class BaseConfig(object):
    """Configuration items common across all config types"""
    ENV = 'DEV'
    DEBUG = False
    TESTING = False

    VERSION = metadata.version('preboot_lander')
    logger.info(f'Starting Scraper Webapp. Env: {ENV} Version: {VERSION} Debug: {DEBUG} Testing: {TESTING}...')
    PORT = 5000
    # Stuff for frontend
    STATIC_DIR_PATH = '../static'
    TEMPLATE_DIR_PATH = '../templates'

    if not os.environ.get('PREBOOT_SECRET'):
        raise ValueError('SECRET_KEY not detected.')
    else:
        logger.debug('Obtaining existing secret key.')
        SECRET_KEY = os.environ.get('PREBOOT_SECRET')


class DevelopmentConfig(BaseConfig):
    """Configuration for development environment"""
    ENV = 'DEV'
    DEBUG = True
    DB_SERVER = 'localhost'
    LOG_LEVEL = 'DEBUG'

    def __init__(self):
        os.environ['PT_ENV'] = self.ENV
        logger.info(f'Log level: {self.LOG_LEVEL}')


class ProductionConfig(BaseConfig):
    """Configuration for production environment"""
    ENV = 'PROD'
    DEBUG = False
    DB_SERVER = '0.0.0.0'
    LOG_LEVEL = 'DEBUG'

    def __init__(self):
        os.environ['PT_ENV'] = self.ENV
        logger.info(f'Log level: {self.LOG_LEVEL}')
