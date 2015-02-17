from fabpolish import sniff, info, local


@sniff(severity='critical', timing='fast')
def find_merge_conflict_leftovers():
    """Find Merge conflict leftovers
    """
    info('Finding merge conflict leftovers...')
    return local("! git grep -P '^(<|=|>){7}(?![<=>])'")


@sniff(severity='major', timing='slow')
def find_php_syntax_errors():
    """Find syntax error in php files
    """
    info('Finding syntax error in php files...')
    return local(
        "git ls-files -z | "
        "grep -PZz '\.(php|phtml)$' | "
        "xargs -0 -n 1 php -l >/tmp/debug"
    )


@sniff(severity='minor', timing='slow')
def find_pep8_violations():
    """Run pep8 python coding standard check
    """
    info('Running coding standards check for python files...')
    return local(
        "git ls-files -z | "
        "grep -PZz '\.py$' | "
        "xargs -0 pep8"
    )
