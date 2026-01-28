#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy and translate 95 local H5 games from "95套H5小游戏源码大合集" into public/games,
clean common third‑party ad scripts, inject GameAdAPI, and update src/data/games.js.

This is a wrapper around 部署95游戏并翻译.py to avoid issues with non‑ASCII filenames.
"""

import importlib

def main():
    try:
        mod = importlib.import_module('部署95游戏并翻译')
    except ModuleNotFoundError:
        # Fallback: if module name cannot be imported due to encoding, try execfile style
        import runpy
        runpy.run_path('部署95游戏并翻译.py', run_name='__main__')
        return

    if hasattr(mod, 'main'):
        mod.main()
    else:
        # If the module has no main(), just import side‑effects
        pass


if __name__ == '__main__':
    main()

