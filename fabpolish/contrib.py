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


@sniff(severity='major', timing='fast')
def python_code_analyzer():
    """Running static code analyzer"""
    info('Running static code analyzer')
    return local(
        "git ls-files -z | "
        "grep -PZz '\.py$' | "
        "grep -PZvz 'fabfile.py' | "
        "xargs -0 pyflakes"
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


@sniff(severity='major', timing='fast')
def fix_file_permission():
    """Fixing permissions for files"""
    info('Fixing permissions for files')
    return local(
        "git ls-files -z | "
        "grep -PvZz '\.sh$' | "
        "xargs -0 chmod -c 0664 > /dev/null 2>&1"
    )


@sniff(severity='major', timing='fast')
def fix_script_permission():
    # Fix script permissions
    info('Fixing script permissions...')
    return local(
        "git ls-files -z | "
        "grep -PZz '\.sh$' | "
        "xargs -0 -r chmod 0775 >/dev/null 2>&1"
    )


@sniff(severity='major', timing='fast')
def fix_white_space():
    info('Fixing whitespace errors...')
    return local(
        "git ls-files -z | "
        "grep -PZvz '\.(ico|jpg|png|gif|eot|ttf|woff|wav|xlxs)$' | "
        "xargs -0 grep -PlZn '(\\s+$)|(\\t)' | "
        "tee /dev/stderr | "
        "xargs -0 -r sed -i -e 's/\\s\\+$//' "
    )


@sniff(severity='major', timing='fast')
def convert_tab_spaces():
    info('Converting tab to spaces...')
    return local(
        "git ls-files -z | "
        "grep -PZvz '\.(ico|jpg|png|gif|eot|ttf|woff|wav|xlxs)$' | "
        "xargs -0 grep -PlZn '(\\s+$)|(\\t)' | "
        "tee /dev/stderr | "
        "xargs -0 -r sed -i -e 's/\\t/    /g' "
    )


@sniff(severity='critical', timing='fast')
def check_migration_branch():
    """Checking migration branches"""
    info('Checking migration branches...')
    return local("! alembic branches | grep branchpoint")


@sniff(severity='major', timing='fast')
def check_python_debug_info():
    """Check and remove debugging print statements"""
    info('Checking for debug print statements')
    return local(
        "! git ls-files -z | "
        "grep -PZvz 'fabfile.py' | "
        "grep -PZz \.py$ | "
        "xargs -0 grep -Pn \'(?<![Bb]lue|>>> )print\' | "
        "grep -v NOCHECK"
    )


@sniff(severity='major', timing='fast')
def check_php_debug_info():
    info('Checking for var_dump, echo or die statements...')
    return local(
        "! find ./src -name '*.php' -print0 | "
        "xargs -0 egrep -n 'var_dump|echo|die' | grep -v 'NOCHECK'"
    )


@sniff(severity='major', timing='fast')
def check_image_edited():
    # Check if image files have been edited
    info('Checking if image files have been edited...')
    info('Explanation: A new image should be created when '
         'editing images to avoid browser caching')
    branch = local('git rev-parse --abbrev-ref HEAD')
    return local(
        '! git diff master...' + branch +
        ' --name-only --diff-filter=M | ' +
        'grep ".gif\|.png\|.jpg"'
    )


@sniff(severity='critical', timing='fast')
def composer_validate():
    info('Running composer validate...')
    return local('composer validate')


@sniff(severity='major', timing='fast')
def run_eslint():
    info('Running ESLint...')
    return local(
        "git ls-files | "
        "grep '\.js$' | "
        "xargs ./node_modules/eslint/bin/eslint.js"
    )


@sniff(severity='major', timing='fast')
def check_preg_replace():
    info('Checking use of preg_replace...')
    return local(
        "! find src -name '*.php' -print0 | "
        "xargs -0 grep -n 'preg_replace('"
    )
