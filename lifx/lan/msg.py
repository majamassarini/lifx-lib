from typing import Tuple, Union

from lifx import Msg as Parent, Octect
from lifx.lan.header import Header
from lifx.lan import light


class Msg(Parent):
    """
    >>> import lifx
    >>> msg = lifx.lan.Msg.from_bytes(bytearray([0x64, 0x00, 0x00, 0x54, 0x42, 0x52, 0x4B, 0x52, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x00, 0x00, 0x98, 0xFE, 0xB5, 0x2A, 0xD5, 0x77, 0x81, 0x14, 0x3B, 0x00, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0xA0, 0x10, 0xB8, 0x31, 0xD5, 0x77, 0x81, 0x14, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
    >>> (header, body) = msg.decode()
    >>> header.type
    <State.echo_response: 59>
    >>> msg = lifx.lan.Msg.from_bytes([0x32, 0x00, 0x00, 0x54, 0x42, 0x52, 0x4B, 0x52, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x00, 0x00, 0x98, 0xA8, 0xDC, 0x8F, 0xD6, 0x77, 0x81, 0x14, 0x0D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5E, 0x0F])
    >>> (header, body) = msg.decode()
    >>> header.type
    <State.state_host_info: 13>
    >>> msg = lifx.lan.Msg.from_bytes([0x58, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x00, 0xD0, 0x73, 0xD5, 0x12, 0x1A, 0xF1, 0x00, 0x00, 0x4C, 0x49, 0x46, 0x58, 0x56, 0x32, 0x01, 0x00, 0x08, 0x3B, 0xD6, 0xBE, 0x58, 0x3E, 0x39, 0x16, 0x6B, 0x00, 0x00, 0x00, 0x54, 0xD5, 0xBB, 0x05, 0x5B, 0xFF, 0xAC, 0x0D, 0x00, 0x00, 0xFF, 0xFF, 0x42, 0x61, 0x67, 0x6E, 0x6F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    >>> (header, body) = msg.decode()
    >>> str(body)
    'State {power: 65535, hue: 300, saturation: 2, brightness: 100, kelvin: 3500, rgb: (255, 250, 255), label: Bagno}'
    """

    @classmethod
    def encode(cls, header: 'lifx.lan.Header', body: Union[light.GetService,
                                                           light.SetPower,
                                                           light.GetPower,
                                                           light.SetColor,
                                                           light.SetWaveform], addr: str = None, port: int = None) -> \
            'lifx.lan.Msg':
        """
        >>> import lifx
        >>> header = lifx.lan.header.make("set_color_light")
        >>> body = lifx.lan.light.SetColor()
        >>> body.field.color.rgb = (0, 255, 0)
        >>> body.field.color.kelvin = 3500
        >>> body.field.duration = 1024
        >>> msg = lifx.lan.Msg.encode(header, body)
        >>> msg
        [0x31, 0x00, 0x00, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x66, 0x00, 0x00, 0x00, 0x00, 0x55, 0x55, 0xFF, 0xFF, 0xFF, 0xFE, 0xAC, 0x0D, 0x00, 0x04, 0x00, 0x00]

        :param header: a lifx.lan.Header
        :param body: a lifx lan payload
        :param addr: an ip address to associate the message with
        :param port: an ip port to associate the message with
        :return: a lifx.lan.Msg
        """
        l = []
        header.field.protocol = 1024
        for byte in header.bytes:
            octect = Octect()
            octect.value = byte
            l.append(octect)
        if body and hasattr(body, "bytes"):
            for byte in body.bytes:
                octect = Octect()
                octect.value = byte
                l.append(octect)
        size = Octect()
        size.value = len(l)
        l[0] = size
        return cls(l, addr=addr, port=port)

    def decode(self) -> Tuple[Header, Union[light.StateService,
                                            light.StatePower,
                                            light.State]]:
        """
        >>> import lifx
        >>> s = "310000340000000000000000000000000000000000000000000000000000000066000000005555FFFFFFFFAC0D00040000"
        >>> msg = lifx.lan.Msg.from_string(s)
        >>> (header, body) = msg.decode()
        >>> header.type
        <State.set_color_light: 102>
        >>> header.field.size
        49
        >>> header.field.protocol
        1024
        >>> header.field.type
        102
        >>> s = str(body)
        >>> 'SetColor' in s
        True

        :return: a tuple (header, body)
        """
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
