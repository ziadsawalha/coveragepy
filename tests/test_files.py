# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://bitbucket.org/ned/coveragepy/src/default/NOTICE.txt

"""Tests for files.py"""

import os
import os.path

from coverage import files
from coverage.files import (
    TreeMatcher, FnmatchMatcher, ModuleMatcher, PathAliases,
    find_python_files, abs_file, actual_path
)
from coverage.misc import CoverageException
from coverage import env

from tests.coveragetest import CoverageTest


class FilesTest(CoverageTest):
    """Tests of coverage.files."""

    def abs_path(self, p):
        """Return the absolute path for `p`."""
        return os.path.join(os.getcwd(), os.path.normpath(p))

    def test_simple(self):
        self.make_file("hello.py")
        files.set_relative_directory()
        self.assertEqual(files.relative_filename("hello.py"), "hello.py")
        a = self.abs_path("hello.py")
        self.assertNotEqual(a, "hello.py")
        self.assertEqual(files.relative_filename(a), "hello.py")

    def test_peer_directories(self):
        self.make_file("sub/proj1/file1.py")
        self.make_file("sub/proj2/file2.py")
        a1 = self.abs_path("sub/proj1/file1.py")
        a2 = self.abs_path("sub/proj2/file2.py")
        d = os.path.normpath("sub/proj1")
        os.chdir(d)
        files.set_relative_directory()
        self.assertEqual(files.relative_filename(a1), "file1.py")
        self.assertEqual(files.relative_filename(a2), a2)

    def test_filepath_contains_absolute_prefix_twice(self):
        # https://bitbucket.org/ned/coveragepy/issue/194
        # Build a path that has two pieces matching the absolute path prefix.
        # Technically, this test doesn't do that on Windows, but drive
        # letters make that impractical to achieve.
        files.set_relative_directory()
        d = abs_file(os.curdir)
        trick = os.path.splitdrive(d)[1].lstrip(os.path.sep)
        rel = os.path.join('sub', trick, 'file1.py')
        self.assertEqual(files.relative_filename(abs_file(rel)), rel)


class MatcherTest(CoverageTest):
    """Tests of file matchers."""

    def setUp(self):
        super(MatcherTest, self).setUp()
        files.set_relative_directory()

    def assertMatches(self, matcher, filepath, matches):
        """The `matcher` should agree with `matches` about `filepath`."""
        canonical = files.canonical_filename(filepath)
        self.assertEqual(
            matcher.match(canonical), matches,
            "File %s should have matched as %s" % (filepath, matches)
        )

    def test_tree_matcher(self):
        matches_to_try = [
            (self.make_file("sub/file1.py"), True),
            (self.make_file("sub/file2.c"), True),
            (self.make_file("sub2/file3.h"), False),
            (self.make_file("sub3/file4.py"), True),
            (self.make_file("sub3/file5.c"), False),
        ]
        trees = [
            files.canonical_filename("sub"),
            files.canonical_filename("sub3/file4.py"),
            ]
        tm = TreeMatcher(trees)
        self.assertEqual(tm.info(), trees)
        for filepath, matches in matches_to_try:
            self.assertMatches(tm, filepath, matches)

    def test_module_matcher(self):
        matches_to_try = [
            ('test', True),
            ('trash', False),
            ('testing', False),
            ('test.x', True),
            ('test.x.y.z', True),
            ('py', False),
            ('py.t', False),
            ('py.test', True),
            ('py.testing', False),
            ('py.test.buz', True),
            ('py.test.buz.baz', True),
            ('__main__', False),
            ('mymain', True),
            ('yourmain', False),
        ]
        modules = ['test', 'py.test', 'mymain']
        mm = ModuleMatcher(modules)
        self.assertEqual(
            mm.info(),
            modules
        )
        for modulename, matches in matches_to_try:
            self.assertEqual(
                mm.match(modulename),
                matches,
                modulename,
            )

    def test_fnmatch_matcher(self):
        matches_to_try = [
            (self.make_file("sub/file1.py"), True),
            (self.make_file("sub/file2.c"), False),
            (self.make_file("sub2/file3.h"), True),
            (self.make_file("sub3/file4.py"), True),
            (self.make_file("sub3/file5.c"), False),
        ]
        fnm = FnmatchMatcher(["*.py", "*/sub2/*"])
        self.assertEqual(fnm.info(), ["*.py", "*/sub2/*"])
        for filepath, matches in matches_to_try:
            self.assertMatches(fnm, filepath, matches)

    def test_fnmatch_matcher_overload(self):
        fnm = FnmatchMatcher(["*x%03d*.txt" % i for i in range(500)])
        self.assertMatches(fnm, "x007foo.txt", True)
        self.assertMatches(fnm, "x123foo.txt", True)
        self.assertMatches(fnm, "x798bar.txt", False)

    def test_fnmatch_windows_paths(self):
        # We should be able to match Windows paths even if we are running on
        # a non-Windows OS.
        fnm = FnmatchMatcher(["*/foo.py"])
        self.assertMatches(fnm, r"dir\foo.py", True)
        fnm = FnmatchMatcher([r"*\foo.py"])
        self.assertMatches(fnm, r"dir\foo.py", True)


class PathAliasesTest(CoverageTest):
    """Tests for coverage/files.py:PathAliases"""

    run_in_temp_dir = False

    def assert_mapped(self, aliases, inp, out):
        """Assert that `inp` mapped through `aliases` produces `out`.

        `out` is canonicalized first, since aliases always produce
        canonicalized paths.

        """
        self.assertEqual(aliases.map(inp), files.canonical_filename(out))

    def assert_not_mapped(self, aliases, inp):
        """Assert that `inp` mapped through `aliases` is unchanged."""
        self.assertEqual(aliases.map(inp), inp)

    def test_noop(self):
        aliases = PathAliases()
        self.assert_not_mapped(aliases, '/ned/home/a.py')

    def test_nomatch(self):
        aliases = PathAliases()
        aliases.add('/home/*/src', './mysrc')
        self.assert_not_mapped(aliases, '/home/foo/a.py')

    def test_wildcard(self):
        aliases = PathAliases()
        aliases.add('/ned/home/*/src', './mysrc')
        self.assert_mapped(aliases, '/ned/home/foo/src/a.py', './mysrc/a.py')

        aliases = PathAliases()
        aliases.add('/ned/home/*/src/', './mysrc')
        self.assert_mapped(aliases, '/ned/home/foo/src/a.py', './mysrc/a.py')

    def test_no_accidental_match(self):
        aliases = PathAliases()
        aliases.add('/home/*/src', './mysrc')
        self.assert_not_mapped(aliases, '/home/foo/srcetc')

    def test_multiple_patterns(self):
        aliases = PathAliases()
        aliases.add('/home/*/src', './mysrc')
        aliases.add('/lib/*/libsrc', './mylib')
        self.assert_mapped(aliases, '/home/foo/src/a.py', './mysrc/a.py')
        self.assert_mapped(aliases, '/lib/foo/libsrc/a.py', './mylib/a.py')

    def test_cant_have_wildcard_at_end(self):
        aliases = PathAliases()
        msg = "Pattern must not end with wildcards."
        with self.assertRaisesRegex(CoverageException, msg):
            aliases.add("/ned/home/*", "fooey")
        with self.assertRaisesRegex(CoverageException, msg):
            aliases.add("/ned/home/*/", "fooey")
        with self.assertRaisesRegex(CoverageException, msg):
            aliases.add("/ned/home/*/*/", "fooey")

    def test_no_accidental_munging(self):
        aliases = PathAliases()
        aliases.add(r'c:\Zoo\boo', 'src/')
        aliases.add('/home/ned$', 'src/')
        self.assert_mapped(aliases, r'c:\Zoo\boo\foo.py', 'src/foo.py')
        self.assert_mapped(aliases, r'/home/ned$/foo.py', 'src/foo.py')

    def test_paths_are_os_corrected(self):
        aliases = PathAliases()
        aliases.add('/home/ned/*/src', './mysrc')
        aliases.add(r'c:\ned\src', './mysrc')
        self.assert_mapped(aliases, r'C:\Ned\src\sub\a.py', './mysrc/sub/a.py')

        aliases = PathAliases()
        aliases.add('/home/ned/*/src', r'.\mysrc')
        aliases.add(r'c:\ned\src', r'.\mysrc')
        self.assert_mapped(aliases, r'/home/ned/foo/src/sub/a.py', r'.\mysrc\sub\a.py')

    def test_leading_wildcard(self):
        aliases = PathAliases()
        aliases.add('*/d1', './mysrc1')
        aliases.add('*/d2', './mysrc2')
        self.assert_mapped(aliases, '/foo/bar/d1/x.py', './mysrc1/x.py')
        self.assert_mapped(aliases, '/foo/bar/d2/y.py', './mysrc2/y.py')

    def test_dot(self):
        for d in ('.', '..', '../other', '~'):
            aliases = PathAliases()
            aliases.add(d, '/the/source')
            the_file = os.path.join(d, 'a.py')
            the_file = os.path.expanduser(the_file)
            the_file = os.path.abspath(os.path.realpath(the_file))

            assert '~' not in the_file  # to be sure the test is pure.
            self.assert_mapped(aliases, the_file, '/the/source/a.py')


class FindPythonFilesTest(CoverageTest):
    """Tests of `find_python_files`."""

    def test_find_python_files(self):
        self.make_file("sub/a.py")
        self.make_file("sub/b.py")
        self.make_file("sub/x.c")                   # nope: not .py
        self.make_file("sub/ssub/__init__.py")
        self.make_file("sub/ssub/s.py")
        self.make_file("sub/ssub/~s.py")            # nope: editor effluvia
        self.make_file("sub/lab/exp.py")            # nope: no __init__.py
        self.make_file("sub/windows.pyw")
        py_files = set(find_python_files("sub"))
        self.assert_same_files(py_files, [
            "sub/a.py", "sub/b.py",
            "sub/ssub/__init__.py", "sub/ssub/s.py",
            "sub/windows.pyw",
            ])


class WindowsFileTest(CoverageTest):
    """Windows-specific tests of file name handling."""

    run_in_temp_dir = False

    def setUp(self):
        if not env.WINDOWS:
            self.skip("Only need to run Windows tests on Windows.")
        super(WindowsFileTest, self).setUp()

    def test_actual_path(self):
        self.assertEquals(actual_path(r'c:\Windows'), actual_path(r'C:\wINDOWS'))
