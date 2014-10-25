DEBUG = True
def verbose(*args):
    if DEBUG is True:
        print("FFP\t", *args)
