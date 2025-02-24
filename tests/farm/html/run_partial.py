# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

import sys

def html_it():
    """Run coverage.py and make an HTML report for partial."""
    import coverage
    cov = coverage.Coverage(branch=True)
    cov.start()
    import partial          # pragma: nested
    cov.stop()              # pragma: nested
    cov.html_report(partial, directory="../html_partial")

runfunc(html_it, rundir="src")

# HTML files will change often.  Check that the sizes are reasonable,
#   and check that certain key strings are in the output.
compare("gold_partial", "html_partial", size_within=10, file_pattern="*.html")
contains("html_partial/partial_py.html",
    '<p id="t8" class="stm run hide_run">',
    '<p id="t11" class="stm run hide_run">',
    '<p id="t14" class="stm run hide_run">',
    # The "if 0" and "if 1" statements are optimized away.
    '<p id="t17" class="pln">',
    )
contains("html_partial/index.html",
    '<a href="partial_py.html">partial.py</a>',
    )
contains("html_partial/index.html",
    '<span class="pc_cov">100%</span>'
    )

clean("html_partial")
