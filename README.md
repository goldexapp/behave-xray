# behave-xray

[![PyPi](https://img.shields.io/pypi/v/behave-xray.png)](https://pypi.python.org/pypi/behave-xray)
[![Build Status](https://travis-ci.com/fundakol/behave-xray.svg?branch=master)](https://travis-ci.com/github/fundakol/behave-xray)

### Installation


```commandline
pip install -U behave-xray
```

or 

```commandline
python setup.py install
```
### Usage 

Add JIRA tags to Gherkin scenario:

```gherkin
# --FILE: tutorial.feature 
@jira.test_plan('JIRA-3')
Feature: showing off behave

  @jira.testcase('JIRA-1')
  Scenario: run a simple test
     Given we have behave installed
      When we implement a test
      Then behave will test it for us!
```

Set system environments (Basic authentication): For Cloud Xray app only
```shell
export client_id=<client_id>
export client_secret=<client_secret>
```

Run tests:

```commandline
behave . -f behave_xray.formatter:XrayFormatter
```
