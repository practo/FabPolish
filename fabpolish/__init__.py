import os
import sys

from functools import wraps

from fabric.main import list_commands
from fabric.api import lcd, local, settings, task, puts, hide
from fabric.colors import green

import fabfile

FABFILE_DIR = os.path.abspath(os.path.dirname(fabfile.__file__))

__version__ = '1.1.0'


def info(text):
    puts(green(text))


def validate_severity(severity):
    severity_options = ['critical', 'major', 'minor', 'info']
    if severity not in severity_options:
        raise ValueError('severity must be one of: ' + str(severity_options))


def validate_timing(timing):
    timing_options = ['slow', 'fast']
    if timing not in timing_options:
        raise ValueError('timing must be one of: ' + str(timing_options))


_sniffs = []


def sniff(*args, **kwargs):
    """ Decorator to collect sniffs and execute on polish
        :param severity: Keyword argument only.
                         One of 'critical', 'major', 'minor', 'info'
                         Default: 'critical'
        :type severity: str
        :param timing: Keyword argument only. One of 'slow', 'fast'
                       Default: 'fast'
        :type timing: str
    """
    DEFAULT_SEVERITY = 'critical'
    DEFAULT_TIMING = 'fast'
    invoked = bool(not args or kwargs)
    severity = kwargs.get('severity', DEFAULT_SEVERITY)
    timing = kwargs.get('timing', DEFAULT_TIMING)
    validate_severity(severity)
    validate_timing(timing)

    def decorator(func):
        @task
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lcd(FABFILE_DIR), settings(hide('running')):
                return func(*args, **kwargs)
        _sniffs.append({
            'severity': severity,
            'timing': timing,
            'function': wrapper
        })
        return wrapper
    return decorator if invoked else decorator(args[0])


@task
def polish(env='dev'):
    """Polish code by running some or all sniffs
    :param env: Environment to determine what all sniffs to run
                Options: 'dev', 'ci'
                Default: 'dev'
    :type env: str

    When environment is 'ci', all the sniffs registered are run.
    When environment is 'dev', only fast-critical and fast-major
    sniffs are run.
    """
    fabric_tasks = list_commands('', 'short')
    results = list()
    with settings(warn_only=True):
        if env == 'ci':
            sniffs_to_run = []
            for sniff in _sniffs:
                if sniff['function'].name not in fabric_tasks:
                    continue
                sniffs_to_run.append(sniff)
        elif env == 'dev':
            sniffs_to_run = []
            for sniff in _sniffs:
                if sniff['function'].name not in fabric_tasks:
                    continue
                if sniff['timing'] != 'fast':
                    continue
                if sniff['severity'] not in ('critical', 'major'):
                    continue
                sniffs_to_run.append(sniff)
        else:
            raise ValueError('env must be one of: ' + str(['dev', 'ci']))
        for sniff in sniffs_to_run:
            results.append(sniff['function']())

    if any(result.failed for result in results):
        sys.exit(1)


def update_sniff(function, severity=None, timing=None):
    if type(function) == str:
        function_name = function
    else:
        function_name = function.name
    for sniff in _sniffs:
        if sniff['function'].name == function_name:
            break
    else:
        raise ValueError('function is not a sniff or is not loaded')
    if severity is not None:
        validate_severity(severity)
        sniff['severity'] = severity
    if timing is not None:
        validate_timing(timing)
        sniff['timing'] = timing


__all__ = [
    'sniff',
    'info',
    'local',
    'polish',
    'update_sniff'
]
