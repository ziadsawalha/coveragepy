"""Tests for coverage.codeunit"""

import os
import sys

from coverage.codeunit import CodeUnit
from coverage.python import PythonCodeUnit

from tests.coveragetest import CoverageTest

# pylint: disable=import-error
# Unable to import 'aa' (No module named aa)


def native(filename):
    """Make `filename` into a native form."""
    return filename.replace("/", os.sep)


class CodeUnitTest(CoverageTest):
    """Tests for coverage.codeunit"""

    run_in_temp_dir = False

    def setUp(self):
        super(CodeUnitTest, self).setUp()
        # Parent class saves and restores sys.path, we can just modify it.
        testmods = self.nice_file(os.path.dirname(__file__), 'modules')
        sys.path.append(testmods)

    def test_filenames(self):
        acu = PythonCodeUnit("aa/afile.py")
        bcu = PythonCodeUnit("aa/bb/bfile.py")
        ccu = PythonCodeUnit("aa/bb/cc/cfile.py")
        self.assertEqual(acu.name, "aa/afile.py")
        self.assertEqual(bcu.name, "aa/bb/bfile.py")
        self.assertEqual(ccu.name, "aa/bb/cc/cfile.py")
        self.assertEqual(acu.flat_rootname(), "aa_afile_py")
        self.assertEqual(bcu.flat_rootname(), "aa_bb_bfile_py")
        self.assertEqual(ccu.flat_rootname(), "aa_bb_cc_cfile_py")
        self.assertEqual(acu.source(), "# afile.py\n")
        self.assertEqual(bcu.source(), "# bfile.py\n")
        self.assertEqual(ccu.source(), "# cfile.py\n")

    def test_odd_filenames(self):
        acu = PythonCodeUnit("aa/afile.odd.py")
        bcu = PythonCodeUnit("aa/bb/bfile.odd.py")
        b2cu = PythonCodeUnit("aa/bb.odd/bfile.py")
        self.assertEqual(acu.name, "aa/afile.odd.py")
        self.assertEqual(bcu.name, "aa/bb/bfile.odd.py")
        self.assertEqual(b2cu.name, "aa/bb.odd/bfile.py")
        self.assertEqual(acu.flat_rootname(), "aa_afile_odd_py")
        self.assertEqual(bcu.flat_rootname(), "aa_bb_bfile_odd_py")
        self.assertEqual(b2cu.flat_rootname(), "aa_bb_odd_bfile_py")
        self.assertEqual(acu.source(), "# afile.odd.py\n")
        self.assertEqual(bcu.source(), "# bfile.odd.py\n")
        self.assertEqual(b2cu.source(), "# bfile.py\n")

    def test_modules(self):
        import aa
        import aa.bb
        import aa.bb.cc

        acu = PythonCodeUnit(aa)
        bcu = PythonCodeUnit(aa.bb)
        ccu = PythonCodeUnit(aa.bb.cc)
        self.assertEqual(acu.name, native("aa.py"))
        self.assertEqual(bcu.name, native("aa/bb.py"))
        self.assertEqual(ccu.name, native("aa/bb/cc.py"))
        self.assertEqual(acu.flat_rootname(), "aa_py")
        self.assertEqual(bcu.flat_rootname(), "aa_bb_py")
        self.assertEqual(ccu.flat_rootname(), "aa_bb_cc_py")
        self.assertEqual(acu.source(), "# aa\n")
        self.assertEqual(bcu.source(), "# bb\n")
        self.assertEqual(ccu.source(), "")  # yes, empty

    def test_module_files(self):
        import aa.afile
        import aa.bb.bfile
        import aa.bb.cc.cfile

        acu = PythonCodeUnit(aa.afile)
        bcu = PythonCodeUnit(aa.bb.bfile)
        ccu = PythonCodeUnit(aa.bb.cc.cfile)
        self.assertEqual(acu.name, native("aa/afile.py"))
        self.assertEqual(bcu.name, native("aa/bb/bfile.py"))
        self.assertEqual(ccu.name, native("aa/bb/cc/cfile.py"))
        self.assertEqual(acu.flat_rootname(), "aa_afile_py")
        self.assertEqual(bcu.flat_rootname(), "aa_bb_bfile_py")
        self.assertEqual(ccu.flat_rootname(), "aa_bb_cc_cfile_py")
        self.assertEqual(acu.source(), "# afile.py\n")
        self.assertEqual(bcu.source(), "# bfile.py\n")
        self.assertEqual(ccu.source(), "# cfile.py\n")

    def test_comparison(self):
        acu = CodeUnit("aa/afile.py")
        acu2 = CodeUnit("aa/afile.py")
        zcu = CodeUnit("aa/zfile.py")
        bcu = CodeUnit("aa/bb/bfile.py")
        assert acu == acu2 and acu <= acu2 and acu >= acu2
        assert acu < zcu and acu <= zcu and acu != zcu
        assert zcu > acu and zcu >= acu and zcu != acu
        assert acu < bcu and acu <= bcu and acu != bcu
        assert bcu > acu and bcu >= acu and bcu != acu

    def test_egg(self):
        # Test that we can get files out of eggs, and read their source files.
        # The egg1 module is installed by an action in igor.py.
        import egg1
        import egg1.egg1

        # Verify that we really imported from an egg.  If we did, then the
        # __file__ won't be an actual file, because one of the "directories"
        # in the path is actually the .egg zip file.
        self.assert_doesnt_exist(egg1.__file__)

        ecu = PythonCodeUnit(egg1)
        eecu = PythonCodeUnit(egg1.egg1)
        self.assertEqual(ecu.source(), u"")
        self.assertEqual(eecu.source().split("\n")[0], u"# My egg file!")
