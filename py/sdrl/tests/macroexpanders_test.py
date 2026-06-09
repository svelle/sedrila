# pytest tests
import unittest.mock
import types

import base as b
import sdrl.macros as macros
import sdrl.macroexpanders

import tests.testbase as tb


prot_expected_output = """
<table class='vwr-table'>
<tr><td><span class='prot-counter prot-skip-color'>1.</span> <span class='vwr-front'></span> <span class='vwr-userhost'>u@h</span> <span class='vwr-dir'>~/d</span> <span class='vwr-time'>12:34:56</span> <span class='vwr-num'> 88 </span> <span class='vwr-back'></span></td></tr>
<tr><td><span class='vwr-cmd'>$ cmd arg</span></td></tr>
<tr><td><span class='vwr-output'>out1</span></td></tr>
<tr><td><span class='vwr-output'>out2</span></td></tr>
<tr><td><span class='prot-counter prot-skip-color'>2.</span> <span class='vwr-front'></span> <span class='vwr-userhost'>u@h</span> <span class='vwr-dir'>~/d</span> <span class='vwr-time'>12:34:59</span> <span class='vwr-num'> 89 </span> <span class='vwr-back'></span></td></tr>
<tr><td><span class='vwr-cmd'>$ cmd2</span></td></tr>
<tr><td><span class='vwr-output'>out3</span></td></tr>
</table>

"""


class CourseDummy:
    altdir = "altdir/ch"
    itreedir = "altdir/itree.zip"
    chapterdir = "ch"

    @staticmethod
    def get_part(filename, partname):
        return types.SimpleNamespace(name=partname, outputfile=f"{partname}.html")


class CourseWithoutItreeDummy(CourseDummy):
    itreedir = None


def test_expand_prot():
    with tb.TempDirEnvironContextMgr():
        prot = "u@h ~/d 12:34:56 88\n$ cmd arg\nout1\nout2\nu@h ~/d 12:34:59 89\n$ cmd2\nout3"
        b.spit("myfile.prot", prot)
        call = macros.Macrocall(unittest.mock.MagicMock(), "notask.md", "notask",
                                f"[PROT::myfile.prot]", "PROT", "myfile.prot", None)
        prot_output = sdrl.macroexpanders.expand_prot(CourseDummy(), call)
        print(prot_output)
        assert prot_output == prot_expected_output


def test_includefile_path():
    # ----- prepare:
    b._testmode_reset()
    # ----- perform tests:
    def func(arg: str, itree_mode=False) -> str:
        call = macros.Macrocall(None, "ch/chapter/group/task.md", "task",
                                f"[INCLUDE::{arg}]", "INCLUDE", arg, None)
        return sdrl.macroexpanders.includefile_path(CourseDummy(), call, itree_mode)

    assert func("other") == "ch/chapter/group/other"
    assert func("/other2") == "ch/other2"
    assert func("ALT:other") == "altdir/ch/chapter/group/other"
    assert func("ALT:/other2") == "altdir/ch/other2"
    assert func("ALT:") == "altdir/ch/chapter/group/task.md"
    assert func("ITREE:other") == "altdir/itree.zip/chapter/group/other"
    assert func("ITREE:/other2") == "altdir/itree.zip/other2"
    assert func("ITREE:") == "altdir/itree.zip/chapter/group/task.md"
    assert func("other", itree_mode=True) == "altdir/itree.zip/chapter/group/other"
    assert func("/other2", itree_mode=True) == "altdir/itree.zip/other2"


def test_partrefmanual_uses_explicit_link_text():
    call = macros.Macrocall(None, "notask.md", "notask",
                            "[PARTREFMANUAL::Target::manual text]",
                            "PARTREFMANUAL", "Target", "manual text")
    assert sdrl.macroexpanders.expand_partref(CourseDummy(), call) == (
        "<a href='Target.html' class='partref-link'>manual text</a>"
    )


def test_expand_treeref_without_itreedir_returns_placeholder():
    b._testmode_reset()
    call = macros.Macrocall(None, "ch/chapter/group/task.md", "task",
                            "[TREEREF::solution.py]", "TREEREF", "solution.py", None)
    assert sdrl.macroexpanders.expand_treeref(CourseWithoutItreeDummy(), call) == (
        "<span class='treeref-prefix'></span>"
        "<span class='treeref'>???</span>"
        "<span class='treeref-suffix'></span>"
    )
