#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: setup.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

from distutils.core import setup
import idserver

setup(name='idserver',
      version=idserver.version,
      description='A python server to manage and distribute a collection of pre-defined ids on client requests.',
      author='Korepwx',
      author_email='public@korepwx.com',
      url='https://github.com/korepwx/idserver',
      license='BSD',
      packages=['idserver'],
)
