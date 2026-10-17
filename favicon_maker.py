#!/usr/bin/env python3
"""Run favicon-maker from a clone without installing it:  python3 favicon_maker.py logo.png"""

import importlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

if __name__ == '__main__':
    from favicon_maker.cli import main

    main()
else:
    # Imported, not run: the repo root is on sys.path (e.g. `python -m pytest`)
    # and this file shadows the real package. Hand over to the one in src/.
    del sys.modules[__name__]
    sys.modules[__name__] = importlib.import_module(__name__)
