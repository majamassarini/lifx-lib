from __future__ import annotations

import abc
from collections.abc import Iterable
from typing import TYPE_CHECKING
from ctypes import c_uint8, LittleEndianStructure, Union

if TYPE_CHECKING:
    import lifx


class Msg(abc.ABC, list):
    """Abstract base class for a LIFX message represented as a list of Octect values."""

    def __init__(
        self,
        octects: Iterable["lifx.Octect"],
        addr: str = None,
        port: int = None,
    ):
        """
        A list of lifx.Octect optionally linked to a IP (addr, port)

        :param octects: an empty list or a list of lifx.Octect
        :param addr: an IP address bound to this message
        :param port: an IP port bound to this message
        """
        super(Msg, self).__init__(octects)
        self._addr = addr
        self._port = port

    @classmethod
    def from_string(
        cls, s: str, addr: str = None, port: int = None
    ) -> "lifx.Msg":
        """
        >>> import lifx
        >>> s = "310000340000000000000000000000000000000000000000000000000000000066000000005555FFFFFFFFAC0D00040000"
        >>> message = lifx.Msg.from_string(s, "1.1.1.1", 1)
        >>> message
        [0x31, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x00, 0x00, 0x00, 0x00, 0x55, 0x55, 0xFF, 0xFF, 0xFF, 0xFF, 0xAC, 0x0D, 0x00, 0x04, 0x00, 0x00]
        >>> message[0].nibble.high = 0x3
        >>> message[0].nibble.low = 0x1
        >>> message.addr
        '1.1.1.1'
        >>> message.port
        1

        Create a lifx.Msg from its string representation

        :param s: a string representation of a Lifx message
        :param addr: an IP address bound to this message
        :param port: an IP port bound to this message
        :return: a lifx.Msg
        """
        high_nibbles = [
            int(nibble, 16) for index, nibble in enumerate(s) if not index % 2
        ]
        low_nibbles = [
            int(nibble, 16) for index, nibble in enumerate(s) if index % 2
        ]
        return cls(
            map(
                lambda high_nibble, low_nibble: Octect(
                    Nibbles(high=high_nibble, low=low_nibble)
                ),
                high_nibbles,
                low_nibbles,
            ),
            addr=addr,
            port=port,
        )

    @classmethod
    def from_bytes(
        cls, byts: bytes, addr: str = None, port: int = None
    ) -> "lifx.Msg":
        """
        >>> import lifx
        >>> bts = bytes([0xFF, 0xFE, 0xFD])
        >>> message = lifx.Msg.from_bytes(bts, "1.1.1.1", 1)
        >>> message
        [0xFF, 0xFE, 0xFD]
        >>> message[1].nibble.high = 0xF
        >>> message[1].nibble.low = 0xE
        >>> message.addr
        '1.1.1.1'
        >>> message.port
        1

        Create a lifx.Msg from its byte representation

        :param byts: a bytearray
        :param addr: an IP address bound to this message
        :param port: an IP port bound to this message
        :return: a lifx.Msg
        """
        return cls([Octect(value=byte) for byte in byts], addr=addr, port=port)

    @classmethod
    @abc.abstractmethod
    def encode(
        cls,
        header: "lifx.Msg",
        body: "lifx.Msg",
        addr: str = None,
        port: int = None,
    ) -> "lifx.Msg":
        """Encode a header and body into a complete LIFX message."""
        ...

    @abc.abstractmethod
    def decode(self) -> tuple:
        """Decode this message into a (header, body) tuple."""
        ...

    def __bytes__(self):
        return bytes([octect.value for octect in self])

    @property
    def addr(self):
        """The IP address bound to this message."""
        return self._addr

    @property
    def port(self):
        """The IP port bound to this message."""
        return self._port


class Nibbles(LittleEndianStructure):
    """A little-endian structure holding the high and low nibbles of a byte."""

    _fields_ = [("low", c_uint8, 4), ("high", c_uint8, 4)]


class Octect(Union):
    """
    A union representing a single byte as either a raw value or a pair of nibbles.

    >>> o = Octect(Nibbles(high=1, low=0))
    >>> o.value
    16
    >>> o = Octect(value=45)
    """

    _fields_ = [("nibble", Nibbles), ("value", c_uint8)]

    def __repr__(self, *args, **kwargs):
        return "0x%02X" % self.value
