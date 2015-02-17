from fabpolish import polish, update_sniff
from fabpolish.contrib import (
    find_merge_conflict_leftovers,
    find_pep8_violations
)

update_sniff(find_pep8_violations, severity='major', timing='fast')
