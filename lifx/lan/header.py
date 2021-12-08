import logging
from ctypes import c_uint8, c_uint32, c_uint16, c_uint64, LittleEndianStructure, Union
from enum import IntEnum


class _Header(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        # frame
        ("size", c_uint16),
        ("protocol", c_uint16, 12),
        ("addressable", c_uint16, 1),
        ("tagged", c_uint16, 1),
        ("origin", c_uint16, 2),
        ("source", c_uint32),
        # frame address
        ("target", c_uint8 * 8),
        ("reserved", c_uint8 * 6),
        ("res_required", c_uint8, 1),
        ("ack_required", c_uint8, 1),
        ("", c_uint8, 6),
        ("sequence", c_uint8),
        # protocol header
        ("", c_uint64),
        ("type", c_uint16),
        ("", c_uint16),
    ]


class Header(Union):
    """
    >>> import lifx
    >>> h = lifx.lan.Header()
    >>> h.bytes[0] = 0x31
    >>> h.bytes[3] = 0x34
    >>> h.bytes[32] = 0x66
    >>> h.field.size
    49
    >>> h.field.protocol
    1024
    >>> h.field.type
    102
    >>> h.field.type = lifx.lan.Header.State.echo_request
    >>> h.field.type
    58
    """

    _fields_ = [("bytes", c_uint8 * 36), ("field", _Header)]

    class State(IntEnum):
        get_service = (2,)
        state_service = (3,)
        get_host_info = (12,)
        state_host_info = (13,)
        get_host_firmware = (14,)
        state_host_firmware = (15,)
        get_wifi_info = (16,)
        state_wifi_info = (17,)
        get_wifi_firmware = (18,)
        state_wifi_firmware = (19,)
        get_power = (20,)
        set_power = (21,)
        state_power = (22,)
        get_label = (23,)
        set_label = (24,)
        state_label = (25,)
        get_version = (32,)
        state_version = (33,)
        get_info = (34,)
        state_info = (35,)
        acknowledgement = (45,)
        get_location = (48,)
        state_location = (50,)
        get_group = (51,)
        state_group = (53,)
        echo_request = (58,)
        echo_response = (59,)
        get_light = (101,)
        set_color_light = (102,)
        set_waveform_light = (103,)
        state_light = (107,)
        get_power_light = (116,)
        set_power_light = (117,)
        state_power_light = (118,)
        get_infrared = (120,)
        state_infrared = (121,)
        set_infrared = (122,)
        set_color_zone = (501,)
        get_color_zone = (502,)
        state_zone = (503,)
        state_multi_zone = 506

    @property
    def type(self) -> "lifx.lan.Header.State":
        """
        Get type of state

        :return: lifx.lan.header.State
        """
        try:
            state = self.State(self.field.type)
        except ValueError as e:
            logging.error(e)
            state = str(self.field.type)
        return state

    @type.setter
    def type(self, value: "lifx.lan.Header.State"):
        """
        Set type of state

        :param value: lifx.lan.header.State
        """
        self.field.type = value

    def __str__(self):
        return "Lifx Header type {}".format(self.field.type)


def make(state: str) -> "lifx.lan.Header":
    """
    Make a lifx.lan.Header given a State string representation

    :param state: a state string representation
    :return: lifx.lan.Header
    """
    header = Header()
    header.type = Header.State[state]
    header.field.tagged = 1
    header.field.addressable = 1
    header.field.ack_required = 1
    return header
