from FuzzyFilePath.common.config import config

IGNORE = ["cache"]

def log(*args):
	if config["LOG"]:
		print("FFP\t", *args)

def verbose(*args):
    if config["DEBUG"] is True and not args[0] in IGNORE:
        print("FFP\t", *args)
