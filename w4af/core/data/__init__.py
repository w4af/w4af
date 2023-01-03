# Translation hack. Needed for tests completion.
try:
    _('blah')
except:
    import builtins
    builtins.__dict__['_'] = lambda x: x
