# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

"""Tests for coverage.py's improved tokenizer."""

import os.path
import re

from coverage import env
from coverage.phystokens import source_token_lines, source_encoding
from coverage.phystokens import neuter_encoding_declaration
from coverage.python import get_python_source

from tests.coveragetest import CoverageTest


SIMPLE = u"""\
# yay!
def foo():
  say('two = %d' % 2)
"""

MIXED_WS = u"""\
def hello():
        a="Hello world!"
\tb="indented"
"""

HERE = os.path.dirname(__file__)


class PhysTokensTest(CoverageTest):
    """Tests for coverage.py's improved tokenizer."""

    run_in_temp_dir = False

    def check_tokenization(self, source):
        """Tokenize `source`, then put it back together, should be the same."""
        tokenized = ""
        for line in source_token_lines(source):
            text = "".join(t for _, t in line)
            tokenized += text + "\n"
        # source_token_lines doesn't preserve trailing spaces, so trim all that
        # before comparing.
        source = source.replace('\r\n', '\n')
        source = re.sub(r"(?m)[ \t]+$", "", source)
        tokenized = re.sub(r"(?m)[ \t]+$", "", tokenized)
        self.assertMultiLineEqual(source, tokenized)

    def check_file_tokenization(self, fname):
        """Use the contents of `fname` for `check_tokenization`."""
        self.check_tokenization(get_python_source(fname))

    def test_simple(self):
        self.assertEqual(list(source_token_lines(SIMPLE)),
            [
                [('com', "# yay!")],
                [('key', 'def'), ('ws', ' '), ('nam', 'foo'), ('op', '('),
                            ('op', ')'), ('op', ':')],
                [('ws', '  '), ('nam', 'say'), ('op', '('),
                            ('str', "'two = %d'"), ('ws', ' '), ('op', '%'),
                            ('ws', ' '), ('num', '2'), ('op', ')')]
            ])
        self.check_tokenization(SIMPLE)

    def test_tab_indentation(self):
        # Mixed tabs and spaces...
        self.assertEqual(list(source_token_lines(MIXED_WS)),
            [
                [('key', 'def'), ('ws', ' '), ('nam', 'hello'), ('op', '('),
                            ('op', ')'), ('op', ':')],
                [('ws', '        '), ('nam', 'a'), ('op', '='),
                            ('str', '"Hello world!"')],
                [('ws', '        '), ('nam', 'b'), ('op', '='),
                            ('str', '"indented"')],
            ])

    def test_tokenize_real_file(self):
        # Check the tokenization of a real file (large, btw).
        real_file = os.path.join(HERE, "test_coverage.py")
        self.check_file_tokenization(real_file)

    def test_stress(self):
        # Check the tokenization of a stress-test file.
        stress = os.path.join(HERE, "stress_phystoken.tok")
        self.check_file_tokenization(stress)
        stress = os.path.join(HERE, "stress_phystoken_dos.tok")
        self.check_file_tokenization(stress)


# The default encoding is different in Python 2 and Python 3.
if env.PY3:
    DEF_ENCODING = "utf-8"
else:
    DEF_ENCODING = "ascii"


ENCODING_DECLARATION_SOURCES = [
    # Various forms from http://www.python.org/dev/peps/pep-0263/
    b"# coding=cp850\n\n",
    b"#!/usr/bin/python\n# -*- coding: cp850 -*-\n",
    b"#!/usr/bin/python\n# vim: set fileencoding=cp850:\n",
    b"# This Python file uses this encoding: cp850\n",
    b"# This file uses a different encoding:\n# coding: cp850\n",
]

class SourceEncodingTest(CoverageTest):
    """Tests of source_encoding() for detecting encodings."""

    run_in_temp_dir = False

    def test_detect_source_encoding(self):
        for source in ENCODING_DECLARATION_SOURCES:
            self.assertEqual(
                source_encoding(source),
                'cp850',
                "Wrong encoding in %r" % source
            )

    def test_detect_source_encoding_not_in_comment(self):
        if env.PYPY and env.PY3:
            # PyPy3 gets this case wrong. Not sure what I can do about it,
            # so skip the test.
            self.skip("PyPy3 is wrong about non-comment encoding. Skip it.")
        # Should not detect anything here
        source = b'def parse(src, encoding=None):\n    pass'
        self.assertEqual(source_encoding(source), DEF_ENCODING)

    def test_detect_source_encoding_on_second_line(self):
        # A coding declaration should be found despite a first blank line.
        source = b"\n# coding=cp850\n\n"
        self.assertEqual(source_encoding(source), 'cp850')

    def test_dont_detect_source_encoding_on_third_line(self):
        # A coding declaration doesn't count on the third line.
        source = b"\n\n# coding=cp850\n\n"
        self.assertEqual(source_encoding(source), DEF_ENCODING)

    def test_detect_source_encoding_of_empty_file(self):
        # An important edge case.
        self.assertEqual(source_encoding(b""), DEF_ENCODING)

    def test_bom(self):
        # A BOM means utf-8.
        source = b"\xEF\xBB\xBFtext = 'hello'\n"
        self.assertEqual(source_encoding(source), 'utf-8-sig')

        # But it has to be the only authority.
        source = b"\xEF\xBB\xBF# coding: cp850\n"
        with self.assertRaises(SyntaxError):
            source_encoding(source)


class NeuterEncodingDeclarationTest(CoverageTest):
    """Tests of phystokens.neuter_encoding_declaration()."""

    run_in_temp_dir = False

    def test_neuter_encoding_declaration(self):
        for source in ENCODING_DECLARATION_SOURCES:
            neutered = neuter_encoding_declaration(source.decode("ascii"))
            neutered = neutered.encode("ascii")
            self.assertEqual(
                source_encoding(neutered),
                DEF_ENCODING,
                "Wrong encoding in %r" % neutered
            )
