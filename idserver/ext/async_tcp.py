#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: idserver/ext/async_tcp.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

"""
Asynchronized TCP concurrency server.
"""

import logging

from tornado.tcpserver import TCPServer
from tornado.ioloop import IOLoop

from .._protocol import Protocol


class TcpIdServerConn(object):
    """Manage a connection with remote client."""

    def __init__(self, stream, addr, protocol):
        self.stream = stream
        self.addr = addr
        self.protocol = protocol

    def doRespond(self, data):
        """Callback when client data has arrived."""
        logging.debug('recv from %s' % (self.addr, ))
        rspdata = self.protocol.handle(data)
        logging.debug('send %s to %s' % (rspdata, self.addr))
        self.stream.write('%s\n' % rspdata, self.doRead)

    def doRead(self):
        """Read from client and give response."""
        self.stream.read_until('\n', self.doRespond)


class TcpIdServer(TCPServer):
    """TCP server to grant ids to connected clients.

    The communication is not blocking even if no free id is available.
    Server will tell clients the missing of id immediately.

    :param idpool: The pool of id to be granted.
    :param host: The interface for this server to listen.
    :param port: The port for this server to listen.
    """

    def __init__(self, idpool, host, port):
        super(TcpIdServer, self).__init__()

        # create the protocol
        self._protocol = Protocol(idpool)
        # record the parameters
        self.host = host
        self.port = port
        # get the logger instance
        self.logger = logging.getLogger(__name__)

    def handle_stream(self, stream, address):
        TcpIdServerConn(stream, address, self._protocol).doRead()

    def run_forever(self):
        """Run the server on given (host, port)."""
        # bind the interface
        self.listen(self.port, self.host)

        # run tornado IO loop
        IOLoop.instance().start()
