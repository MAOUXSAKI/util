def _init():
    if '_global_dict' not in globals().keys():
        global _global_dict
        _global_dict = {}


def set_value(name, value):
    _init()
    _global_dict[name] = value


def get_value(name, defValue=None):
    _init()
    try:
        return _global_dict[name]
    except KeyError:
        return defValue

