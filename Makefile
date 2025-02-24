# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

# Makefile for utility work on coverage.py.

default:
	@echo "* No default action *"

clean:
	-rm -f *.pyd */*.pyd
	-rm -f *.so */*.so
	-PYTHONPATH=. python tests/test_farm.py clean
	-rm -rf build coverage.egg-info dist htmlcov
	-rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc */*/*/*/*.pyc */*/*/*/*/*.pyc
	-rm -f *.pyo */*.pyo */*/*.pyo */*/*/*.pyo */*/*/*/*.pyo */*/*/*/*/*.pyo
	-rm -f *.bak */*.bak */*/*.bak */*/*/*.bak */*/*/*/*.bak */*/*/*/*/*.bak
	-rm -f *$$py.class */*$$py.class */*/*$$py.class */*/*/*$$py.class */*/*/*/*$$py.class */*/*/*/*/*$$py.class
	-rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ */*/*/*/__pycache__ */*/*/*/*/__pycache__
	-rm -f coverage/*,cover
	-rm -f MANIFEST
	-rm -f .coverage .coverage.* coverage.xml .metacov* .noseids
	-rm -f tests/zipmods.zip
	-rm -rf tests/eggsrc/build tests/eggsrc/dist tests/eggsrc/*.egg-info
	-rm -f setuptools-*.egg distribute-*.egg distribute-*.tar.gz
	-rm -rf doc/_build doc/_spell

sterile: clean
	-rm -rf .tox*

LINTABLE = coverage igor.py setup.py tests

lint:
	-pylint $(LINTABLE)
	python -m tabnanny $(LINTABLE)
	python igor.py check_eol

spell:
	-pylint --disable=all --enable=spelling $(LINTABLE)

pep8:
	pep8 --filename=*.py --ignore=E401,E301 --repeat $(LINTABLE)

test:
	tox -e py27 $(ARGS)

metacov:
	COVERAGE_COVERAGE=yes tox $(ARGS)

metahtml:
	python igor.py combine_html

# Kitting

kit:
	python setup.py sdist --formats=gztar,zip

wheel:
	tox -c tox_wheels.ini

kit_upload:
	twine upload dist/*

winkit:
	tox -c tox_winkits.ini

kit_local:
	cp -v dist/* `awk -F "=" '/find-links/ {print $$2}' ~/.pip/pip.conf`

pypi:
	python setup.py register

install:
	python setup.py install

DEVINST_FILE = coverage.egg-info/PKG-INFO
devinst: $(DEVINST_FILE)
$(DEVINST_FILE): coverage/tracer.c
	-rm coverage/tracer.pyd
	python setup.py develop

uninstall:
	-rm -rf $(PYHOME)/lib/site-packages/coverage*
	-rm -rf $(PYHOME)/scripts/coverage*

# Documentation

SPHINXBUILD = sphinx-build
SPHINXOPTS = -a -E doc
WEBHOME = ~/web/stellated/pages/code/coverage

docreqs:
	pip install -r doc/requirements.txt

px:
	$(SPHINXBUILD) -b px $(SPHINXOPTS) doc/_build/px
	rm doc/_build/px/search.px
	python doc/_ext/px_cleaner.py doc/_build/px/*.px

dochtml:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) doc/_build/html
	@echo
	@echo "Build finished. The HTML pages are in doc/_build/html."

docspell:
	$(SPHINXBUILD) -b spelling $(SPHINXOPTS) doc/_spell

publish: px
	rm -f $(WEBHOME)/*.px
	cp doc/_build/px/*.px $(WEBHOME)
	rm -f $(WEBHOME)/sample_html/*.*
	cp doc/sample_html/*.* $(WEBHOME)/sample_html

publishbeta: px
	rm -f $(WEBHOME)/beta/*.px
	mkdir -p $(WEBHOME)/beta
	cp doc/_build/px/*.px $(WEBHOME)/beta
	rm -f $(WEBHOME)/sample_html_beta/*.*
	mkdir -p $(WEBHOME)/sample_html_beta
	cp doc/sample_html_beta/*.* $(WEBHOME)/sample_html_beta
