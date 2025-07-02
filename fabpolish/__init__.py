import os
import sys
import subprocess

from functools import wraps

from fabric import task
from fabric import Connection
from invoke import Collection

import fabfile

FABFILE_DIR = os.path.abspath(os.path.dirname(fabfile.__file__))

__version__ = '1.2.0'


def info(text):
    print(f"\033[32m{text}\033[0m")  # Green color equivalent


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
        def wrapper(c, *args, **kwargs):
            # Create a local connection for executing commands
            with Connection('localhost') as conn:
                # Change to fabfile directory
                original_cwd = os.getcwd()
                os.chdir(FABFILE_DIR)
                try:
                    return func(conn, *args, **kwargs)
                finally:
                    os.chdir(original_cwd)
        _sniffs.append({
            'severity': severity,
            'timing': timing,
            'function': wrapper
        })
        return wrapper
    return decorator if invoked else decorator(args[0])


def local(c, command):
    """Execute a local command using Fabric 2.x Connection"""
    result = c.local(command, hide=True)
    return result


@task
def polish(c, env='dev'):
    """Polish code by running some or all sniffs
    :param env: Environment to determine what all sniffs to run
                Options: 'dev', 'ci'
                Default: 'dev'
    :type env: str

    When environment is 'ci', all the sniffs registered are run.
    When environment is 'dev', only fast-critical and fast-major
    sniffs are run.
    """
    # Get available tasks from the current collection
    collection = Collection.from_module(fabfile)
    fabric_tasks = list(collection.task_names)
    
    results = list()
    
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
    
    # Create a connection for executing tasks
    with Connection('localhost') as conn:
        for sniff in sniffs_to_run:
            try:
                result = sniff['function'](conn)
                results.append(result)
            except Exception as e:
                # Create a failed result object
                class FailedResult:
                    def __init__(self, exception):
                        self.failed = True
                        self.exited = 1
                        self.exception = exception
                results.append(FailedResult(e))

    if any(hasattr(result, 'failed') and result.failed for result in results):
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
