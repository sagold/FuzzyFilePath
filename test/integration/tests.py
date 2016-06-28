"""
	Loads all integration tests within this folder
	- In order to be loaded each test-file must have "_test" appended
	- Tests are stored and dumped by the file name (without test)
"""
import os
import glob
import importlib


tests = []


modules = glob.glob(os.path.dirname(__file__) + "/*_test.py")
modules = [os.path.basename(f)[:-3] for f in modules]

for f in modules:
	lib = importlib.import_module("FuzzyFilePath.test.integration." + f)
	tests.append(lib.Test(f[:-5]))