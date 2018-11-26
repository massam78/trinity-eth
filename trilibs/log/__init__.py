# --*-- coding : utf-8 --*--
"""
Package : 

Author  : Trinity Core Team

MIT License

Copyright (c) 2018 Trinity

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import copy
import logging.config


__all__ = ['init_logger']

LOG = logging.getLogger(__name__)

# This is a default configuration for Trinity system.
# DO NOT CHANGE THIS CONFIGURATION!!!!!
# Any developers want to set the log configuration, he/she could use BasicConfig
# to configure it.
log_default_settings = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(pathname)s line %(lineno)d '
                      '%(levelname)s :%(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG'
        }
    }
}

log_settings = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'formatter': {
            'format': '[%(asctime)s] %(pathname)s line %(lineno)d '
                      '%(levelname)s :%(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'cloghandler.ConcurrentRotatingFileHandler',
            'filename': 'trinity.log',
            'formatter': 'standard',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 10
        }
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG'
        }
    },
}


class BasicConfig(object):
    """
    Descriptions: Generate one basic dictionary as default configuration of
                  trinity LOG system.
    """
    def __init__(self):
        """
        Description: Constructor for logging system basic configuration
        """
        # use
        self.basic_config = copy.deepcopy(log_default_settings)
        logging.config.dictConfig(self.basic_config)

    def setup(self, path=None, file_name=None, level=logging.DEBUG,
              log_format=None, handlers=None, **kwargs):
        """
        Description: Setup the user loggers
        :param path: The path where saved the logs if file handler is set
        :param file_name: The log file name
        :param level: Log level settings. Please refer to the logging package.
        :param log_format: Define the log output format. Please refer to class
                           'Formatter' defined in the logging package.
        :param handlers:
        :param kwargs:
        :return:
        """

        # Finally, use the new dict to configure the loggers
        logging.config.dictConfig(self.basic_config)

    def _parse_handlers(self):
        pass

    def _parse_loggers(self):
        pass

    def _parse_formatter(self):
        pass

    def __parse_file_path(self):
        pass


def init_logger(level=logging.DEBUG, path=None, file_name=None,
                log_handler=None, handler='default'):
    """

    :param level:       set the log level. Please refer to logging package
    :param path:        the path where saving the log file
    :param file_name:   log file name
    :param log_handler: new key word under the log_settings['loggers']
    :param handler:     print the log to file or console. currently it support
                        'default' and 'console' options.
    :return:
    """
    logging.basicConfig(stream="logging.StreamHandler")
    # add new handler inside the loggers
    if log_handler and log_handler not in log_settings['loggers'].keys():
        # This log system just provides 2 handlers: console and default.
        # Customers could add new handlers under keyword "handlers" in
        # log_settings to configure new one.
        log_settings['loggers'][log_handler] = \
            {'handlers': ['default'], 'level': 'DEBUG'}

    # set the logger's log level
    for logger_module in log_settings['loggers'].keys():
        # This system use debug level as default value.
        # if
        log_settings['loggers'][logger_module]['level'] = \
            logging.getLevelName(level) if level else logging.DEBUG

        # is
        if handler and handler not in \
                log_settings['loggers'][logger_module]['handlers']:

            # add logger handlers in the loggers
            handler_list = log_settings['loggers'][logger_module]['handlers']
            if isinstance(handler_list, list):
                handler_list.append(handler)

    # set log path
    log_path = path if path else './temp'
    file_name = file_name if file_name else 'trinity.log'

    # create the log folder
    try:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
    except Exception as error:
        LOG.exception('Failed to set log path. Exception'.format(error))
        log_path = '.'
    finally:
        log_settings['handlers']['default']['filename'] = '{}{}{}'\
            .format(log_path, os.sep, file_name)

    # set logger configuration
    logging.config.dictConfig(log_settings)


final_init_logger = BasicConfig().setup

final_init_logger()
LOG.debug('test')