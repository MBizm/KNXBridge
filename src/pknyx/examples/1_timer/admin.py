#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import sys


def main():
    os.environ.setdefault("PKNYX_DEVICE_PATH", os.path.join(os.path.dirname(__file__), "timer"))

    from pknyx.tools.adminUtility import AdminUtility

    AdminUtility().execute()


if __name__ == "__main__":
    main()
