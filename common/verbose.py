from common.config import config

IGNORE = []

def log(*args):
	if config["LOG"]:
		for arg in args:
			print(arg)

def verbose(*args):
    if config["DEBUG"] is True and not args[0] in IGNORE:
        for arg in args:
			print(arg)
