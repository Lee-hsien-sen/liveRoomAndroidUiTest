#!/usr/bin/python
# -*- coding: utf-8 -*-

def _init():
    global _global_dict
    _global_dict = {}

def set_value(name, value):
    #_global_dict[name] = value
    _global_dict[name] = value

def update_value(name, data):
    if name:
        _global_dict[name].update(data)
    else:
        _global_dict.update(data)

def get_value(name, defValue=None):
    try:
        return _global_dict[name]
    except KeyError:
        return defValue
def get_dict():
    return _global_dict