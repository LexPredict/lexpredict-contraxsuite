"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

import logging
import types

from celery.utils.log import get_logger

from django.conf import settings

# Project imports
from apps.common import redis
from apps.common.models import AppVar

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# add App vars for project-level loggers
for logger_name, logger_data in settings.LOGGING['loggers'].items():
    AppVar.set(
        'Logging',
        f'logger:{logger_name}:log_level',
        logger_data['level'],
        f'Custom log level for "{logger_name}" logger.')


# add App vars for celery loggers
celery_logger_names = ['celery', 'celery.beat', 'celery.task', 'celery.worker',
                       'celery.worker.request', 'celery.pool']
for logger_name in celery_logger_names:
    logger = get_logger(logger_name)
    AppVar.set(
        'Logging',
        f'logger:{logger_name}:log_level',
        logging._levelToName.get(logger.level),
        f'Custom log level for "{logger.name}" logger.')


ENABLE_DB_CONSOLE_LOGGING = AppVar.set(
    'Logging',
    'logger:django.db.backends:log_to_console',
    False,
    'Enable logging db sql queries to console.')


def reset_loggers_level():
    """
    Reset loggers' level from AppVar
    """

    def getEffectiveLevel(self):
        """
        Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        logger = self

        # custom logic
        # cannot use AppVar due to circular import issue
        app_var_level = redis.pop(f'app_var:Logging:logger:{logger.name}:log_level')
        if app_var_level:
            app_var_level = app_var_level.upper()
            if app_var_level in logging._levelToName.values():
                logger.setLevel(app_var_level)

                # log sql to console
                if logger.name == 'django.db.backends':
                    handler = logging.StreamHandler()
                    handler.setLevel(logger.level)
                    logger_handler_classes = [i.__class__ for i in logger.handlers]
                    if redis.pop(f'app_var:Logging:logger:{logger.name}:log_to_console') is True:
                        if handler.__class__ not in logger_handler_classes:
                            logger.addHandler(handler)
                    else:
                        logger.handlers = [i for i in logger.handlers if i.__class__ != handler.__class__]
        # end custom logic

        while logger:
            if logger.level:
                return logger.level
            logger = logger.parent
        return logging.NOTSET

    # reset Project loggers
    for logger_name in settings.LOGGING['loggers']:
        logger = logging.getLogger(logger_name)
        logger.getEffectiveLevel = types.MethodType(getEffectiveLevel, logger)

    # reset celery loggers
    for logger_name in celery_logger_names:
        logger = get_logger(logger_name)
        logger.getEffectiveLevel = types.MethodType(getEffectiveLevel, logger)


reset_loggers_level()
