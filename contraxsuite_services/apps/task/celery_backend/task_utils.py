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

from datetime import datetime
from typing import Union, List

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from celery.states import PENDING

_PRECEDENCE_NON_PROPAGATE_ERRORS = [
    'SUCCESS',
    'FAILURE',
    None,
    'REVOKED',
    'STARTED',
    'RECEIVED',
    'REJECTED',
    'RETRY',
    'PENDING',
]

_PRECEDENCE_PROPAGATE_ERRORS = [
    'SUCCESS',
    None,
    'STARTED',
    'RECEIVED',
    'PENDING',
    'REVOKED'
    'REJECTED',
    'RETRY',
    'FAILURE'
]

_PRECEDENCE_LOOKUP_NON_PROPAGATE_ERRORS = dict(
    zip(_PRECEDENCE_NON_PROPAGATE_ERRORS, range(0, len(_PRECEDENCE_NON_PROPAGATE_ERRORS))))

_PRECEDENCE_LOOKUP_PROPAGATE_ERRORS = dict(
    zip(_PRECEDENCE_PROPAGATE_ERRORS, range(0, len(_PRECEDENCE_PROPAGATE_ERRORS))))


def precedence_propagating_exceptions(state: str):
    try:
        return _PRECEDENCE_LOOKUP_PROPAGATE_ERRORS[state]
    except:
        return None


def precedence_non_propagating_exceptions(state: str):
    try:
        return _PRECEDENCE_LOOKUP_NON_PROPAGATE_ERRORS[state]
    except:
        return None


def precedence(state: str, propagate_exceptions: bool):
    state_precedence = _PRECEDENCE_LOOKUP_PROPAGATE_ERRORS \
        if propagate_exceptions else _PRECEDENCE_LOOKUP_NON_PROPAGATE_ERRORS
    try:
        return state_precedence[state]
    except KeyError:
        return state_precedence[None]


def calc_state(all_states: List[str], propagate_exceptions: bool) -> str:
    return max(all_states, key=lambda state: precedence(state, propagate_exceptions))


def get_date_done(all_dates_done: List[datetime]) -> Union[None, datetime]:
    try:
        return max(all_dates_done)
    except TypeError:
        return None


def revoke_task(_task, wait=False, timeout=None):
    if getattr(_task, 'children', None) is not None:
        for child_task in _task.children:
            revoke_task(child_task)
    if getattr(_task, 'status', None) == PENDING:
        try:
            _task.revoke(terminate=True, wait=wait, timeout=timeout)
        except RuntimeError as e:
            if "Acquire on closed pool" in str(e):
                # TODO: define what we should do in this case
                # TODO: celery bug?
                pass
            else:
                raise e
