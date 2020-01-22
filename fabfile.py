""" This is a testing file. """
from fabpolish import update_sniff
from fabpolish.contrib import find_pep8_violations

update_sniff(find_pep8_violations, severity='major', timing='fast')
