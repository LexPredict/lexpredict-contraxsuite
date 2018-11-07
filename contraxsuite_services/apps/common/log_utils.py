import logging

logger = logging.getLogger(__name__)


class ProcessLogger:
    def set_progress_steps_number(self, steps):
        raise NotImplemented()

    def step_progress(self):
        raise NotImplemented()

    def info(self, message: str):
        raise NotImplemented()

    def error(self, message: str, field_code: str = None):
        raise NotImplemented()


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
