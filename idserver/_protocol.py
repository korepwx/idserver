#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: idserver/_protocol.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

import json
import socket
import logging

from ._helpers import is_ipv4
from ._compact import inet_pton


class Protocol(object):
    """Class to represent the server protocol."""

    def __init__(self, idpool):
        self.idpool = idpool

    def handle(self, data):
        """Execute str `data`, and return str response."""
        try:
            reqdata = json.loads(data)
            if reqdata['action'] == 'get':
                ret = self.idpool.acquire(reqdata['owner'], reqdata['expire'])
                if not ret:
                    return json.dumps({'error': 1, 'message': 'id exhausted'})
                return json.dumps({'error': 0, 'value': ret})
            elif reqdata['action'] == 'put':
                self.idpool.release(reqdata['owner'])
                return json.dumps({'error': 0})
            else:
                raise RuntimeError('Action "%s" is not recognized.' %
                                   reqdata['action'])
        except KeyError, ex:
            return json.dumps({
                'error': 1,
                'message': "KeyError: '%s'" % ex.message
            })
        except Exception, ex:
            logging.exception('Error handle "%s"' % data)
            return json.dumps({'error': 1, 'message': ex.message})


class SocketIdClient(object):
    """Base socket client to acquire ids from socket server.

    :param identity: The identity of this client.
    :param host: The host of id server.
    :param port: The port of id server.
    :param timeout: Timeout of the client to wait for results. default 10.
    """

    def __init__(self, host, port, timeout=10):
        # determine whether host is ipv4 address or ipv6 address
        self.inet_type = socket.AF_INET
        if not is_ipv4(host):
            try:
                inet_pton(host, socket.AF_INET6)
            except Exception:
                pass
            else:
                self.inet_type = socket.AF_INET6
        # record the parameters
        self.host = host
        self.port = port
        self.timeout = timeout

    def _sendrecv(self):
        """Dummy method for send request and recv response."""
        raise NotImplementedError()

    def acquire(self, name, expire):
        """Get an id from server, given owner `name` and `expire` time.

        :param name: The name of this client. Server will tend to respond with
            the same id if `name` is same.
        :param expire: Seconds before this id to expire.
        :raise RuntimeError: if remote server tells any error message.
        :raise Exception: if network error takes place.
        """
        rspdata = json.loads(self._sendrecv(json.dumps({
            'action': 'get', 'owner': name, 'expire': expire
        })))
        if rspdata['error'] != 0:
            raise RuntimeError(rspdata['message'])
        return rspdata['value']

    def release(self, name):
        """Put an id back to server, given owner `name`."""
        rspdata = json.loads(self._sendrecv(json.dumps({
            'action': 'put', 'owner': name
        })))
        if rspdata['error'] != 0:
            raise RuntimeError(rspdata['message'])
