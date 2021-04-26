import json
from typing import Union
import logging

import requests
from requests.auth import AuthBase
from behave_xray.model import TestExecution
from os import environ

TEST_EXECUTION_ENDPOINT = 'https://xray.cloud.xpand-it.com/api/v2/import/execution'
AUTHENTICATION_URL = 'https://xray.cloud.xpand-it.com/api/v2/authenticate'

class XrayError(Exception):
    """Custom exception for Jira XRAY"""


class XrayPublisher:

    @property
    def endpoint_url(self) -> str:
        return TEST_EXECUTION_ENDPOINT
    @property
    def authentication_url(self) -> str:
        return AUTHENTICATION_URL

    def parser(self, data):
        test_key_list = []
        test_keys = [test['testKey'] for test in data]
        print(test_keys)
        key_exist = []
        for tests in data:
            if test_keys.count(tests['testKey']) <= 1:
                test_key_list.append(tests)
            elif test_keys.count(tests['testKey']) > 1 and tests['testKey'] not in key_exist:
                key_exist.append(tests['testKey'])
                examples = []
                test_dict = dict()
                test_dict['testKey'] = tests['testKey']
                test_dict['comment'] = tests['comment']
                failed_comments = ''
                scenario_no = test_keys.count(tests['testKey'])
                for test in data:
                    if tests['testKey'] == test['testKey']:
                        examples.append(test['status'])
                        test_dict['examples'] = examples
                        if test['status'] == 'FAILED':
                            failed_comments += '\n----------\n'
                            failed_comments += 'Scenario no. ' + str(scenario_no) + ' ------ ' + test['testKey']
                            failed_comments += '\n----------\n'
                            failed_comments += test['comment']
                            test_dict['comment'] = failed_comments
                        scenario_no = scenario_no - 1
                test_dict['status'] = 'PASSED' if all(elem == 'PASSED' for elem in examples) else 'FAILED'
                test_dict['examples'].reverse()
                test_key_list.append(test_dict)
        return test_key_list

    def publish_data(self, auth: AuthBase, data: dict) -> dict:

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'
                   }
        auth_param ={ "client_id": environ["client_id"],"client_secret": environ["client_secret"] }
        auth_param = json.dumps(auth_param)
        token = requests.request(method='POST',url=self.authentication_url, headers=headers, data =auth_param)
        token = token.text.strip('"')
        token = "Bearer " + token
        data1 = json.dumps(data)
        data2= json.loads(data1)
        data['tests']=self.parser(data=data2['tests'])
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'Authorization': token
                   }
        response = requests.request(method='POST', url=self.endpoint_url, headers=headers, data=json.dumps(data))
        try:
            response.raise_for_status()
        except Exception as e:
            raise XrayError(e)
        return response.json()

    def publish(self, test_execution: TestExecution) -> None:
        try:
            result = self.publish_data(self.endpoint_url, test_execution.as_dict())
        except XrayError as e:
            print('Could not publish to Jira:', e)
        else:
            key = result['key']
            print('Uploaded results to XRAY Test Execution:', key)

