from FuzzyFilePath.common.config import config

IGNORE = ["view", "query"]

def verbose(*args):
    if config["DEBUG"] is True and not args[0] in IGNORE:
        print("FFP\t", *args)
