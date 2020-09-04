from ctypes import c_uint8, LittleEndianStructure, Union

from lifx.lan import light
from lifx.lan.header import Header


class Msg(list):
    """
    >>> s = "310000340000000000000000000000000000000000000000000000000000000066000000005555FFFFFFFFAC0D00040000"
    >>> msg = Msg.from_string(s)
    >>> (head, body) = msg.decode()
    >>> head.field.size
    49
    >>> head.field.protocol
    1024
    >>> head.field.type
    102
    >>> s = str(body)
    >>> 'SetColor' in s
    True
    >>> msg = Msg.encode(head, body)
    >>> print(msg)
    [0x31, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x00, 0x00, 0x00, 0x00, 0x55, 0x55, 0xFF, 0xFF, 0xFF, 0xFF, 0xAC, 0x0D, 0x00, 0x04, 0x00, 0x00]
    >>> msg = Msg.from_bytes([0x58, 0x00, 0x00, 0x54, 0xB9, 0x71, 0x5D, 0x07, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x00, 0x4D, 0x18, 0x52, 0x42, 0x1E, 0xB5, 0xFC, 0x82, 0x14, 0x6B, 0x00, 0x00, 0x00, 0x71, 0x7E, 0xCC, 0x4C, 0x09, 0x57, 0xAC, 0x0D, 0x00, 0x00, 0xFF, 0xFF, 0x4C, 0x49, 0x46, 0x58, 0x20, 0x42, 0x75, 0x6C, 0x62, 0x20, 0x31, 0x32, 0x31, 0x61, 0x66, 0x31, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    >>> (header, body) = msg.decode()
    >>> header.type
    <State.state_light: 107>
    >>> body.field.color.hue
    32369
    >>> body.field.color.saturation
    19660
    >>> body.field.color.brightness
    22281
    >>> body.field.color.kelvin
    3500
    >>> body.field.power
    65535
    >>> body.field.color.rgb
    (61, 87, 86)
    >>> msg = Msg.from_bytes([0x64, 0x00, 0x00, 0x54, 0x42, 0x52, 0x4B, 0x52, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x00, 0x00, 0x98, 0xFE, 0xB5, 0x2A, 0xD5, 0x77, 0x81, 0x14, 0x3B, 0x00, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0xA0, 0x10, 0xB8, 0x31, 0xD5, 0x77, 0x81, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    >>> (header, body) = msg.decode()
    >>> header.type
    <State.echo_response: 59>
    >>> msg = Msg.from_bytes([0x32, 0x00, 0x00, 0x54, 0x42, 0x52, 0x4B, 0x52, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x00, 0x00, 0x98, 0xA8, 0xDC, 0x8F, 0xD6, 0x77, 0x81, 0x14, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5E, 0x0F])
    >>> (header, body) = msg.decode()
    >>> header.type
    <State.state_host_info: 13>
    """

    def __init__(self, *args, addr=None, port=None, **kwargs):
        super(Msg, self).__init__(*args, **kwargs)
        self._addr = addr
        self._port = port

    @staticmethod
    def from_string(s, addr=None, port=None):
        high_nibbles = [int(nibble, 16) for index, nibble in enumerate(s) if not index % 2]
        low_nibbles = [int(nibble, 16) for index, nibble in enumerate(s) if index % 2]
        return Msg(map(lambda high_nibble, low_nibble: Octect(Nibbles(high=high_nibble, low=low_nibble)), high_nibbles, low_nibbles),
                   addr=addr, port=port)

    @staticmethod
    def from_bytes(bytes, addr=None, port=None):
        return Msg([Octect(value=byte) for byte in bytes], addr=addr, port=port)

    @staticmethod
    def encode(header, body, addr=None, port=None):
        l = []
        header.field.protocol = 1024
        for byte in header.bytes:
            octect = Octect()
            octect.value = byte
            l.append(octect)
        if body:
            for byte in body.bytes:
                octect = Octect()
                octect.value = byte
                l.append(octect)
        size = Octect()
        size.value = len(l)
        l[0] = size
        return Msg(l, addr=addr, port=port)

    def decode(self):
        header = Header()
        for index, octect in enumerate(self[0:36]):
            header.bytes[index] = octect.value

        body = None
        if header.type == Header.State.get_service:
            body = light.GetService()
        if header.type == Header.State.state_service:
            body = light.StateService()
        elif header.type == Header.State.get_light:
            body = light.Get()
        elif header.type == Header.State.state_light:
            body = light.State()
        elif header.type == Header.State.set_color_light:
            body = light.SetColor()
        elif header.type == Header.State.set_waveform_light:
            body = light.SetWaveform()
        elif header.type == Header.State.get_power_light:
            body = light.GetPower()
        elif header.type == Header.State.set_power_light:
            body = light.SetPower()
        elif header.type == Header.State.state_power_light:
            body = light.StatePower()

        if body:
            for index, octect in enumerate(self[36:]):
                body.bytes[index] = octect.value
        else:
            body = self[36:]

        return header, body

    def __bytes__(self):
        return bytes([octect.value for octect in self])

    @property
    def addr(self):
        return self._addr

    @property
    def port(self):
        return self._port


class Nibbles(LittleEndianStructure):
    _fields_ = [('low', c_uint8, 4),
                ('high', c_uint8, 4)]


class Octect(Union):
    """
    >>> o = Octect(Nibbles(high=1, low=0))
    >>> o.value
    16
    >>> o = Octect(value=45)
    """

    _fields_ = [('nibble', Nibbles),
                ('value', c_uint8)]

    def __repr__(self, *args, **kwargs):
        return "0x%02X" % self.value
