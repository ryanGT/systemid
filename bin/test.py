#! /usr/bin/env python

"""
Program to execute tests using the py.test like interface.

Systemid's testing utilities were completely stolen from the sympy project.
Basically everywhere you see systemid, it used to say ``sympy''.

The advantage over py.test is that it only depends on sympy and should just
work in any circumstances. See "systemid.test?" for documentation.
"""

import os
import sys
from optparse import OptionParser

bintest_dir = os.path.abspath(os.path.dirname(__file__))         # bin/test
systemid_top  = os.path.split(bintest_dir)[0]      # ../
systemid_dir  = os.path.join(systemid_top, 'systemid')  # ../systemid/
if os.path.isdir(systemid_dir):
   sys.path.insert(0, systemid_top)
import systemid

parser = OptionParser()
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
        default=False)
parser.add_option("--pdb", action="store_true", dest="pdb",
        default=False, help="Run post mortem pdb on each failure")
parser.add_option("--no-colors", action="store_false", dest="colors",
        default=True, help="Do not report colored [OK] and [FAIL]")
parser.add_option("-k", dest="kw", help="only run tests matching the given keyword expression", metavar="KEYWORD", default="")
parser.add_option("--tb", dest="tb", help="traceback verboseness (short/no) [default: %default]", metavar="TBSTYLE", default="short")

options, args = parser.parse_args()

ok = systemid.test(*args, **{"verbose": options.verbose, "kw": options.kw,
    "tb": options.tb, "pdb": options.pdb, "colors": options.colors})
if ok:
    sys.exit(0)
else:
    sys.exit(1)
