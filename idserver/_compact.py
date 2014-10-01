#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: idserver/_compact.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

import sys
import socket


PY2 = sys.version_info[0] == 2

if PY2:
    string_types = (str, unicode)
    iteritems = lambda x: x.iteritems()
else:
    string_types = str
    iteritems = lambda x: iter(x.items())


if sys.platform == 'win32':
    def inet_pton(family, addr):
        if family == socket.AF_INET:
            return socket.inet_aton(addr)
        elif family == socket.AF_INET6:
            if '.' in addr:  # a v4 addr
                v4addr = addr[addr.rindex(':') + 1:]
                v4addr = socket.inet_aton(v4addr)
                v4addr = map(lambda x: ('%02X' % ord(x)), v4addr)
                v4addr.insert(2, ':')
                newaddr = addr[:addr.rindex(':') + 1] + ''.join(v4addr)
                return inet_pton(family, newaddr)
            dbyts = [0] * 8  # 8 groups
            grps = addr.split(':')
            for i, v in enumerate(grps):
                if v:
                    dbyts[i] = int(v, 16)
                else:
                    for j, w in enumerate(grps[::-1]):
                        if w:
                            dbyts[7 - j] = int(w, 16)
                        else:
                            break
                    break
            return ''.join((chr(i // 256) + chr(i % 256)) for i in dbyts)
        else:
            raise RuntimeError("What family?")
else:
    from socket import inet_pton
