"""Tests of miscellaneous stuff."""

import sys

from coverage.misc import Hasher, file_be_gone, overrides
from coverage import __version__, __url__
from tests.coveragetest import CoverageTest


class HasherTest(CoverageTest):
    """Test our wrapper of md5 hashing."""

    run_in_temp_dir = False

    def test_string_hashing(self):
        h1 = Hasher()
        h1.update("Hello, world!")
        h2 = Hasher()
        h2.update("Goodbye!")
        h3 = Hasher()
        h3.update("Hello, world!")
        self.assertNotEqual(h1.hexdigest(), h2.hexdigest())
        self.assertEqual(h1.hexdigest(), h3.hexdigest())

    def test_bytes_hashing(self):
        h1 = Hasher()
        h1.update(b"Hello, world!")
        h2 = Hasher()
        h2.update(b"Goodbye!")
        self.assertNotEqual(h1.hexdigest(), h2.hexdigest())

    def test_dict_hashing(self):
        h1 = Hasher()
        h1.update({'a': 17, 'b': 23})
        h2 = Hasher()
        h2.update({'b': 23, 'a': 17})
        self.assertEqual(h1.hexdigest(), h2.hexdigest())


class RemoveFileTest(CoverageTest):
    """Tests of misc.file_be_gone."""

    def test_remove_nonexistent_file(self):
        # It's OK to try to remove a file that doesn't exist.
        file_be_gone("not_here.txt")

    def test_remove_actual_file(self):
        # It really does remove a file that does exist.
        self.make_file("here.txt", "We are here, we are here, we are here!")
        file_be_gone("here.txt")
        self.assert_doesnt_exist("here.txt")

    def test_actual_errors(self):
        # Errors can still happen.
        # ". is a directory" on Unix, or "Access denied" on Windows
        with self.assertRaises(OSError):
            file_be_gone(".")


class SetupPyTest(CoverageTest):
    """Tests of setup.py"""

    run_in_temp_dir = False

    def test_metadata(self):
        status, output = self.run_command_status(
            "python setup.py --description --version --url --author"
            )
        self.assertEqual(status, 0)
        out = output.splitlines()
        self.assertIn("measurement", out[0])
        self.assertEqual(out[1], __version__)
        self.assertEqual(out[2], __url__)
        self.assertIn("Ned Batchelder", out[3])

    def test_more_metadata(self):
        # Let's be sure we pick up our own setup.py
        # CoverageTest.tearDown restores the original sys.path.
        sys.path.insert(0, '')
        from setup import setup_args

        classifiers = setup_args['classifiers']
        self.assertGreater(len(classifiers), 7)
        self.assert_starts_with(classifiers[-1], "Development Status ::")

        long_description = setup_args['long_description'].splitlines()
        self.assertGreater(len(long_description), 7)
        self.assertNotEqual(long_description[0].strip(), "")
        self.assertNotEqual(long_description[-1].strip(), "")


class OverridesTest(CoverageTest):
    """Test plugins.py:overrides."""

    run_in_temp_dir = False

    def test_overrides(self):
        # pylint: disable=missing-docstring
        class SomeBase(object):
            def method1(self):
                pass

            def method2(self):
                pass

        class Derived1(SomeBase):
            def method1(self):
                pass

        self.assertTrue(overrides(Derived1(), "method1", SomeBase))
        self.assertFalse(overrides(Derived1(), "method2", SomeBase))

        class FurtherDerived1(Derived1):
            """Derive again from Derived1, inherit its method1."""
            pass

        self.assertTrue(overrides(FurtherDerived1(), "method1", SomeBase))
        self.assertFalse(overrides(FurtherDerived1(), "method2", SomeBase))

        class FurtherDerived2(Derived1):
            """Override the overridden method."""
            def method1(self):
                pass

        self.assertTrue(overrides(FurtherDerived2(), "method1", SomeBase))
        self.assertFalse(overrides(FurtherDerived2(), "method2", SomeBase))

        class Mixin(object):
            """A mixin that overrides method1."""
            def method1(self):
                pass

        class Derived2(Mixin, SomeBase):
            """A class that gets the method from the mixin."""
            pass

        self.assertTrue(overrides(Derived2(), "method1", SomeBase))
        self.assertFalse(overrides(Derived2(), "method2", SomeBase))
