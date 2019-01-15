import logging
import sys
import traceback

logger = logging.getLogger(__name__)


def render_error(message: str, caused_by: Exception = None) -> str:
    if caused_by:
        exc_type = caused_by.__class__
        exc_obj = caused_by
        exc_tb = caused_by.__traceback__
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
    details = traceback.extract_tb(exc_tb)
    return '{0}\n' \
           'Error: {1}: {2}.\n' \
           'Details: {3}'.format(message, exc_type.__name__, str(exc_obj), '\n'.join([str(d) for d in details]))


class ProcessLogger:
    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str):
        logger.info(message)

    def error(self, message: str, field_code: str = None):
        logger.error(message)


class ErrorCollectingLogger(ProcessLogger):
    def __init__(self) -> None:
        super().__init__()
        self.field_problems = {}
        self.common_problems = list()

    def set_progress_steps_number(self, steps):
        pass

    def step_progress(self):
        pass

    def info(self, message: str):
        logger.info(message)

    def error(self, message: str, field_code: str = None):
        logger.error('{0}: {1}'.format(field_code, message))
        if not field_code:
            self.common_problems.append(message)
            return

        problems = self.field_problems.get(field_code)

        if problems is None:
            problems = list()
            self.field_problems[field_code] = problems
        problems.append(message)

    def get_error(self):
        if self.common_problems or self.field_problems:
            return {'error': {
                'common_problems': self.common_problems,
                'field_problems': self.field_problems
            }}
        else:
            return None

    def raise_if_error(self):
        if not self.common_problems and not self.field_problems:
            return
        else:
            messages = list()  # type: List[str]
            if self.common_problems:
                messages.extend(self.common_problems)
            if self.field_problems:
                messages.extend(['Field: {0}. Error: {1}'.format(field_code, field_error) for field_code, field_error in self.field_problems.items()])
            raise Exception('\n'.join(messages))