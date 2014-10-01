#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: idserver/_helpers.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

"""
This module provides some helper utilities for `idserver`.
"""

import re


def is_ipv4(addr):
    """Check whether `addr` is an IPv4 address?

    :return: True if `addr` is IPv4 address, False otherwise.
    """
    return re.match(r'^\d{1,3}(\.\d{1,3}){3}$', addr)
