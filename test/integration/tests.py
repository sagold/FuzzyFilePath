"""
	Loads all integration tests within this folder
	Each test-file has to be prepended with "_test" in order to be loaded
	Tests are stored and dumped by the file name (without test)
"""
import os
import glob
import importlib


tests = {}


modules = glob.glob(os.path.dirname(__file__) + "/*_test.py")
modules = [ os.path.basename(f)[:-3] for f in modules]

for f in modules:
	lib = importlib.import_module("FuzzyFilePath.test.integration." + f)
	tests[f[:-5]] = lib.tests