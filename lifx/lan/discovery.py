import asyncio
import logging
import socket
import sys

import lifx

from typing import Tuple, Union, Text


Address = Tuple[str, int]


class Discovery(asyncio.DatagramProtocol):

    GET_SERVICE = "get_service"
    GET = "get_light"
    GET_POWER = "get_power_light"

    STATE_SERVICE = "state_service"

    def __init__(self, remote: Address):
        self._loop = asyncio.get_event_loop()
        self._remote = remote
        self._transport = None

        self.logger = logging.getLogger(__name__)

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self._transport = transport
        sock = transport.get_extra_info("socket")  # type: socket.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broadcast()

    def datagram_received(self, data: Union[bytes, Text], addr: Address):
        msg = lifx.lan.Msg.from_bytes(data)
        (header, body) = msg.decode()
        self.logger.info("{} {} from {}".format(header, body, addr))
        if body.state == self.STATE_SERVICE:
            msg = lifx.lan.Msg.encode(lifx.lan.header.make(self.GET), None)
            data = bytes(msg)
            self._transport.sendto(data, addr)

            msg = lifx.lan.Msg.encode(lifx.lan.header.make(self.GET_POWER), None)
            data = bytes(msg)
            self._transport.sendto(data, addr)

    def broadcast(self):
        msg = lifx.lan.Msg.encode(lifx.lan.header.make(self.GET_SERVICE), None)
        data = bytes(msg)
        self._transport.sendto(data, self._remote)
        self._loop.call_later(5, self.broadcast)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    loop = asyncio.get_event_loop()
    coro = loop.create_datagram_endpoint(
        lambda: Discovery(("255.255.255.255", 56700)), local_addr=("0.0.0.0", 56700)
    )
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
