# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

source_path = None

def html_it():
    """Run coverage.py and make an XML report for a."""
    import coverage, coverage.files
    cov = coverage.Coverage()
    cov.start()
    import a            # pragma: nested
    cov.stop()          # pragma: nested
    cov.xml_report(a, outfile="../xml_1/coverage.xml")
    global source_path
    source_path = coverage.files.relative_directory().rstrip('/')

import os
if not os.path.exists("xml_1"):
    os.makedirs("xml_1")

runfunc(html_it, rundir="src")

compare("gold_x_xml", "xml_1", scrubs=[
    (r' timestamp="\d+"', ' timestamp="TIMESTAMP"'),
    (r' version="[-.\w]+"', ' version="VERSION"'),
    (r'<source>\s*.*?\s*</source>', '<source>%s</source>' % source_path),
    (r'/coverage.readthedocs.org/?[-.\w/]*', '/coverage.readthedocs.org/VER'),
    ])
clean("xml_1")
