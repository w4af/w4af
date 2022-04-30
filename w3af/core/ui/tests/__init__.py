try:
    _('blah')
except:
    import builtins
    builtins.__dict__['_'] = lambda x: x


def setUpPackage():
    import builtins
    builtins.__dict__['_'] = lambda x: x
