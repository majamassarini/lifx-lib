import asyncio
import logging

from typing import Iterable, Tuple, Any
from lifx.lan import Msg


class Client(asyncio.DatagramProtocol):
    """
    An asynchronous trivial client example

    Example::

        >>> import asyncio
        >>> import lifx
        >>> import sys
        >>>
        >>> async def process_responses(msg):
        ...     is_on = False
        ...     (header, body) = msg.decode()
        ...     if header.type == lifx.lan.Header.State.acknowledgement:
        ...         print("got an ack")
        ...     elif header.type == lifx.lan.Header.State.state_power_light:
        ...         is_on = body.level == body.ON
        ...         if is_on:
        ...             print("got light is powered")
        ...         else:
        ...             print("got light is not powered")
        >>>
        >>>
        >>> async def create_datagram_endpoint():
        ...     loop_ = asyncio.get_event_loop()
        ...     transport_, protocol_ = await loop_.create_datagram_endpoint(lambda: Client([process_responses]),
        ...                                                                  local_addr=('0.0.0.0', 56700))
        ...     return transport_, protocol_
        >>>
        >>> loop = asyncio.get_event_loop()
        >>> transport, protocol = loop.run_until_complete(loop.create_task(create_datagram_endpoint()))
        >>>
        >>> body = lifx.lan.light.SetPower()
        >>> body.field.level = lifx.lan.light.SetPower.ON
        >>> header = lifx.lan.header.make(body.state)
        >>> msg_on = lifx.lan.Msg.encode(header, body, '172.31.10.245', 56700)
        >>> body.field.level = lifx.lan.light.SetPower.OFF
        >>> msg_off = lifx.lan.Msg.encode(header, body, '172.31.10.245', 56700)
        >>> body = lifx.lan.light.GetPower()
        >>> header = lifx.lan.header.make(body.state)
        >>> msg_get_power = lifx.lan.Msg.encode(header, body, '172.31.10.245', 56700)
        >>> loop.run_until_complete(loop.create_task(protocol.write([msg_on, msg_get_power, msg_off, msg_get_power])))
        got an ack
        got an ack
        got light is powered
        got an ack
        got an ack
        got light is not powered

    """

    def __init__(self, tasks: Iterable[Any]):
        self._loop = asyncio.get_event_loop()
        self._transport = None
        self._tasks = tasks

        self.logger = logging.getLogger(__name__)

    def connection_made(self, transport):
        self._transport = transport
        self.logger.info("Connection made: {}".format(str(self._transport)))

    def connection_lost(self, exc):
        self.logger.error("Connection lost: {}".format(str(exc)))
        self._transport = None

    def error_received(self, exc):
        self.logger.error("Error received: {}".format(str(exc)))

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        msg = Msg.from_bytes(data, addr=addr[0], port=addr[1])
        self.logger.info("read    {}".format(str(msg)))
        for task in self._tasks:
            self._loop.create_task(task(msg))

    async def write(self, msgs: Iterable["lifx.Msg"]):
        for msg in msgs:
            data = bytes(msg)
            self._transport.sendto(data, (msg.addr, msg.port))
            await asyncio.sleep(1)
