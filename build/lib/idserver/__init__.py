#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: idserver/__init__.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file is distributed under 2-Clause BSD License, which can be found in
# LICENSE.txt

"""
    idserver
    ~~~~~~~~

    A central server to manage and rent pre-defined ids to connected clients.
    :copyright: 2014 (c) Korepwx <public@korepwx.com>.
    :license: BSD, see LICENSE for more details.
"""

import time
import json
import socket
import logging

from ._helpers import is_ipv4
from ._compact import iteritems, inet_pton

__all__ = ['IdPool', 'UdpIdServer', 'UdpIdClient']
version = '0.1'

# Max packet size of each request and response for servers and clients
MAX_PACKET = 8192


class IdPool(object):
    """Manage the lifetime of ids.

    :param items: Collection of pre-defined ids for this `IdPool` to manage.
    """

    def __init__(self, items):
        # self.__items = dict(id => expire-timestamp, owner)
        self.__items = {k: (0, None) for k in items}
        # self.__owner_to_id = dict(owner => id)
        self.__owner_to_id = {}

    def acquire(self, owner, seconds_to_expire):
        """Grant id to the `owner` until `seconds_to_expire` later.

        If some id is already granted to `owner`, renew the expire time and
        return the old id.  If no free id is available, return None.

        :param owner: The name of owner.
        :param seconds_to_expire: Seconds for the owner to own this id.
        """
        now_ts = time.time()
        ret = None

        if owner in self.__owner_to_id:
            oid = self.__owner_to_id[owner]
            if self.__items[oid][1] != owner:
                # We respect the owner set in self.__items, so if the owner
                # not match, it means that the id is not owned by this owner
                del self.__owner_to_id[owner]
            else:
                ret = oid

        if not ret:
            # ret not assigned, we must take a new id
            for k, v in iteritems(self.__items):
                if v[0] < now_ts:
                    ret = k
                    break

        if ret:
            self.__items[ret] = (now_ts + seconds_to_expire, owner)
            self.__owner_to_id[owner] = ret

        return ret

    def release(self, owner):
        """Relase the id granted to `owner` now."""
        if owner in self.__owner_to_id:
            oid = self.__owner_to_id[owner]
            if self.__items[oid][1] == owner:
                self.__items[oid] = (0, None)
                del self.__owner_to_id[owner]


class UdpIdServer(object):
    """UDP server to grant ids to connected clients.

    The communication is not blocking even if no free id is available.
    Server will tell clients the missing of id immediately.

    Since the server runs on UDP protocol, it should only serve at a
    rather reliable environment.  If a client shutdown, but the release
    packet is not received by server, the id will hang up until it expires.

    :param idpool: The pool of id to be granted.
    :param host: The interface for this server to listen.
    :param port: The port for this server to listen.
    :param timeout: The timeout of server socket. Server will exit if no
        client connects within this period of time. default -1 (no timeout).
    """

    def __init__(self, idpool, host, port, timeout=-1, backlog=100):
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
        self.idpool = idpool
        self.host = host
        self.port = port
        self.timeout = timeout
        # get the logger instance
        self.logger = logging.getLogger(__name__)

    def _execute(self, data):
        """Execute `data`, and return the response."""
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
            logging.exception('Error execute "%s"' % data)
            return json.dumps({'error': 1, 'message': ex.message})

    def run_forever(self):
        """Run the server on given (host, port)."""
        # create the socket
        server = socket.socket(self.inet_type, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind and listen
        server.bind((self.host, self.port))

        # receive the packets and respond
        while True:
            msg, addr = server.recvfrom(MAX_PACKET)
            logging.debug('recv from %s' % (addr, ))
            rspdata = self._execute(msg)
            logging.debug('send %s to %s' % (rspdata, addr))
            server.sendto(rspdata, addr)

        server.close()


class UdpIdClient(object):
    """UDP client to acquire ids from UDP id server.

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

    def _sendrecv(self, data):
        """Send `data` to server, and recv the response."""
        sck = socket.socket(self.inet_type, socket.SOCK_DGRAM)
        sck.sendto(data, (self.host, self.port))
        return sck.recv(8192)

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
