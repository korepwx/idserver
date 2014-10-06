#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: tcp_server.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

from idserver import IdPool, TcpIdServer

if __name__ == '__main__':
    idp = IdPool('name-%d' % x for x in xrange(10))
    svr = TcpIdServer(idp, '127.0.0.1', 9777)
    svr.run_forever()
