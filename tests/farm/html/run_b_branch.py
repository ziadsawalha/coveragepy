# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

def html_it():
    """Run coverage.py with branches and make an HTML report for b."""
    import coverage
    cov = coverage.Coverage(branch=True)
    cov.start()
    import b            # pragma: nested
    cov.stop()          # pragma: nested
    cov.html_report(b, directory="../html_b_branch")

runfunc(html_it, rundir="src")

# HTML files will change often.  Check that the sizes are reasonable,
#   and check that certain key strings are in the output.
compare("gold_b_branch", "html_b_branch", size_within=10, file_pattern="*.html")
contains("html_b_branch/b_py.html",
    '<span class="key">if</span> <span class="nam">x</span> <span class="op">&lt;</span> <span class="num">2</span>',
    '&nbsp; &nbsp; <span class="nam">a</span> <span class="op">=</span> <span class="num">3</span>',
    '<span class="pc_cov">70%</span>',
    '<span class="annotate" title="no jump to this line number">11</span>',
    '<span class="annotate" title="no jump to this line number">exit</span>',
    '<span class="annotate" title="no jumps to these line numbers">26&nbsp;&nbsp; 28</span>',
    )
contains("html_b_branch/index.html",
    '<a href="b_py.html">b.py</a>',
    '<span class="pc_cov">70%</span>',
    '<td class="right" data-ratio="16 23">70%</td>',
    )

clean("html_b_branch")
