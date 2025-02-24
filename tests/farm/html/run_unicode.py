# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

def html_it():
    """Run coverage.py and make an HTML report for unicode.py."""
    import coverage
    cov = coverage.Coverage()
    cov.start()
    import unicode          # pragma: nested
    cov.stop()              # pragma: nested
    cov.html_report(unicode, directory="../html_unicode")

runfunc(html_it, rundir="src")

# HTML files will change often.  Check that the sizes are reasonable,
#   and check that certain key strings are in the output.
compare("gold_unicode", "html_unicode", size_within=10, file_pattern="*.html")
contains("html_unicode/unicode_py.html",
    '<span class="str">&quot;&#654;d&#729;&#477;b&#592;&#633;&#477;&#652;o&#596;&quot;</span>',
    )

contains_any("html_unicode/unicode_py.html",
    '<span class="str">&quot;db40,dd00: x&#56128;&#56576;&quot;</span>',
    '<span class="str">&quot;db40,dd00: x&#917760;&quot;</span>',
    )

clean("html_unicode")
