import re
from collections import defaultdict
from os import environ

from behave.formatter.base import Formatter
from behave.model import Status as ScenarioStatus
from behave_xray.model import XrayStatus, TestCase, TestExecution
from behave_xray.xray_publisher import XrayPublisher

_scenario_keys = defaultdict(lambda: TestCase())


def get_test_execution_tag(tag):
    match = re.match(r"jira\.test_execution\('(.+)'\)", tag)
    if match:
        return match.group(1)
    else:
        return None


def get_test_plan_tag(tag):
    match = re.match(r"jira\.test_plan\('(.+)'\)", tag)
    if match:
        return match.group(1)
    else:
        return None


def get_test_case_tag(tag):
    match = re.match(r"allure\.testcase\('(.+)'\)", tag)
    if match:
        return match.group(1)
    match = re.match(r"jira\.testcase\('(.+)'\)", tag)
    if match:
        return match.group(1)
    else:
        return None


class XrayFormatter(Formatter):
    description = 'Jira XRAY formatter'

    def __init__(self, stream, config):
        super().__init__(stream, config)
        self.current_feature = None
        self.current_scenario = None
        self.test_execution = TestExecution()
        jira_url = environ["XRAY_API_BASE_URL"]
        auth = (environ["XRAY_API_USER"], environ["XRAY_API_PASSWORD"])
        self.xray_publisher = XrayPublisher(base_url=jira_url, auth=auth)

    def feature(self, feature):
        self.current_feature = feature
        if feature.tags:
            for tag in feature.tags:
                te = get_test_execution_tag(tag)
                if te:
                    self.test_execution.test_execution_key = te
                tp = get_test_plan_tag(tag)
                if tp:
                    self.test_execution.test_plan_key = tp

    def scenario(self, scenario):
        self.current_scenario = scenario
        if scenario.tags:
            for tag in scenario.tags:
                tk = get_test_case_tag(tag)
                if tk:
                    _scenario_keys[scenario].test_key = tk

    def result(self, result):
        if self.current_scenario.status == ScenarioStatus.untested:
            return

        _scenario_keys[self.current_scenario].duration = result.duration

        if self.current_scenario.status == ScenarioStatus.passed:
            _scenario_keys[self.current_scenario].status = XrayStatus.PASS
        if result.status == ScenarioStatus.failed:
            _scenario_keys[self.current_scenario].status = XrayStatus.FAIL
            _scenario_keys[self.current_scenario].comment = result.error_message
        if result.status == ScenarioStatus.untested:
            _scenario_keys[self.current_scenario].status = XrayStatus.TODO
        if result.status == ScenarioStatus.skipped:
            _scenario_keys[self.current_scenario].status = XrayStatus.ABORTED
            _scenario_keys[self.current_scenario].comment = self.current_scenario.skip_reason

    def eof(self):
        if self.config.dry_run:
            return

        for scenario, xray in _scenario_keys.items():
            if xray.test_key:
                self.test_execution.append(xray)
        self.xray_publisher.publish(self.test_execution)