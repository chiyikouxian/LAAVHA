#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""包入口，使 ``python -m laavha_viz`` 可直接启动。"""

import sys

from .app import main

if __name__ == "__main__":
    sys.exit(main())
