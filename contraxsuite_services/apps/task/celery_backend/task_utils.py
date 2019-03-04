from datetime import datetime
from typing import Union, List

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
    if getattr(_task, 'status', None) == 'PENDING':
        try:
            _task.revoke(terminate=True, wait=wait, timeout=timeout)
        except RuntimeError as e:
            if "Acquire on closed pool" in str(e):
                # TODO: define what we should do in this case
                # TODO: celery bug?
                pass
            else:
                raise e
