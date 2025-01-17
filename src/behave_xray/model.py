import datetime as dt
import enum
from typing import Dict, List, Union, Any

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class XrayStatus(str, enum.Enum):
    TODO = 'TODO'
    EXECUTING = 'EXECUTING'
    PENDING = 'PENDING'
    PASS = 'PASSED'
    FAIL = 'FAILED'
    ABORTED = 'ABORTED'
    BLOCKED = 'BLOCKED'


class TestCase:

    def __init__(self,
                 test_key: str = None,
                 status: str = XrayStatus.TODO,
                 comment: str = None,
                 duration: float = 0.0):
        self.test_key = test_key
        self.status = XrayStatus(status)
        self.comment = comment or ''
        self.duration = duration

    def as_dict(self) -> Dict[str, str]:
        return dict(testKey=self.test_key,
                    status=self.status,
                    comment=self.comment)

    def __repr__(self):
        return f"{self.__class__.__name__}(test_key='{self.test_key}', status='{self.status}')"

class TestExecution:

    def __init__(self,
                 test_execution_key: str = None,
                 test_plan_key: str = None,
                 user: str = None,
                 revision: str = None,
                 tests: List = None):
        self.test_execution_key = test_execution_key
        self.test_plan_key = test_plan_key or ''
        self.user = user or ''
        self.revision = revision or ''
        self.start_date = dt.datetime.now(tz=dt.timezone.utc)
        self.tests = tests or []

    def append(self, test: Union[dict, TestCase]) -> None:
        if not isinstance(test, TestCase):
            test = TestCase(**test)
        self.tests.append(test)

    def flush(self):
        self.tests = []

    def as_dict(self) -> Dict[str, Any]:
        tests = [test.as_dict() for test in self.tests]
        info = dict(startDate=self.start_date.strftime(DATETIME_FORMAT),
                    finishDate=dt.datetime.now(tz=dt.timezone.utc).strftime(DATETIME_FORMAT))
        data = dict(info=info,
                    tests=tests)
        if self.test_plan_key:
            info['testPlanKey'] = self.test_plan_key
        if self.test_execution_key:
            data['testExecutionKey'] = self.test_execution_key
        return data
