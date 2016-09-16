import FuzzyFilePath.common.settings as settings

IGNORE = ["CurrentFile", "QueryCompletionListener", "search", "Expression"]

def log(*args):
	if settings.get("log"):
		print("FFP\t", *args)

def verbose(*args):
    if settings.get("debug") is True and not args[0] in IGNORE:
        print("FFP\t", *args)

def warn(*args):
	print("FFP -WARNING-\t", *args)

def start_block():
	if settings.get("log") or settings.get("debug"):
		print("")

def end_block():
	if settings.get("log") or settings.get("debug"):
		print("")
