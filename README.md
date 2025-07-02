# Fab Polish

Run various checks against source code using Fabric 2.x

## Installation

`pip install fab-polish`

## Requirements

- Python 3.6+
- Fabric 2.x

## Usage

### Minimal Usage

Create a `fabfile.py` in your source code with the following minimal code:

```python
from fabpolish import polish
from fabpolish.contrib import find_merge_conflict_leftovers
```

Now run `fab polish`. The above example runs a sniff that finds bad merge
commits by checking if symbols like '<<<<<<<' are present in the versioned
files.

### Writing Sniffs

You can create your own sniff by using the sniff decorator:

```python
from fabpolish import polish, sniff, local, info

@sniff(severity='critical', timing='fast')
def check_var_dump(c):
    info("Checking var_dump statements...")
    return local(c, "! git grep 'var_dump'")
```

Severity can be 'critical', 'major', 'minor', 'info'. Default is 'critical'.
Timing can be 'slow', 'fast'. Default is 'fast'.

When using default values, the sniff decorator can be used without the function
call like so:

```python
@sniff
def your_sniff(c):
    # code
```

**Note**: All sniff functions must accept a `c` parameter (the Fabric connection object).

Check https://github.com/practo/FabPolish/blob/master/fabpolish/contrib.py for more examples.

### Modifying Imported Sniffs

The severity, timing values can be altered for any sniff imported from contrib
using `update_sniff` function like follows:

```python
from fabpolish import update_sniff
from fabpolish.contrib import find_pep8_violations

update_sniff(find_pep8_violations, severity='major', timing='fast')
```

### Running All Sniffs

By default `fab polish` runs only fast-critical and fast-major sniffs. In a CI
environment, to run all the sniffs including slow, minor ones, run `fab polish:ci`

## Migration from Fabric3

This version has been updated to support Fabric 2.x instead of fabric3. The main changes are:

- All sniff functions now require a `c` parameter (Fabric connection object)
- The `local()` function now takes the connection as the first parameter
- Task discovery has been updated to use the new Fabric 2.x API
- Color output now uses ANSI escape codes instead of fabric.colors
