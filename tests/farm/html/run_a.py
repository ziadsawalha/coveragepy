# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

def html_it():
    """Run coverage.py and make an HTML report for a."""
    import coverage
    cov = coverage.Coverage()
    cov.start()
    import a            # pragma: nested
    cov.stop()          # pragma: nested
    cov.html_report(a, directory="../html_a")

runfunc(html_it, rundir="src")

# HTML files will change often.  Check that the sizes are reasonable,
#   and check that certain key strings are in the output.
compare("gold_a", "html_a", size_within=10, file_pattern="*.html")
contains("html_a/a_py.html",
    '<span class="key">if</span> <span class="num">1</span> <span class="op">&lt;</span> <span class="num">2</span>',
    '&nbsp; &nbsp; <span class="nam">a</span> <span class="op">=</span> <span class="num">3</span>',
    '<span class="pc_cov">67%</span>'
    )
contains("html_a/index.html",
    '<a href="a_py.html">a.py</a>',
    '<span class="pc_cov">67%</span>',
    '<td class="right" data-ratio="2 3">67%</td>',
    )

clean("html_a")
