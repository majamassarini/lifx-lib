from __future__ import annotations

import sys
import inspect
import colorsys

from enum import IntEnum
from ctypes import (
    c_uint8,
    c_uint32,
    c_float,
    c_uint16,
    c_int16,
    c_uint64,
    LittleEndianStructure,
    Union,
)
from typing import TYPE_CHECKING, Union as TUnion

if TYPE_CHECKING:
    import lifx


class GetService(LittleEndianStructure):
    """A LIFX GetService request message with no payload."""

    _fields_: list = []

    state = "get_service"

    def __str__(self):
        return "GetService"


class _StateService(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("service", c_uint8),
        ("port", c_uint32),
    ]


class StateService(LittleEndianStructure):
    """A LIFX StateService response containing the service type and port."""

    state = "state_service"

    _fields_ = [("field", _StateService), ("bytes", c_uint8 * 52)]

    @property
    def service(self):
        """The service type (only UDP/1 is supported)."""
        return self.field.service

    @service.setter
    def service(self):
        self.field.service = 1  # only udp (1) is allowed

    @property
    def port(self):
        """The UDP port on which the device is listening."""
        return self.field.port

    @port.setter
    def port(self, value):
        self.field.port = value

    def __str__(self):
        return "StateService {{service: {}, port: {}}}".format(
            self.service, self.port
        )


class HSBK(LittleEndianStructure):
    """
    A LIFX HSBK color value holding hue, saturation, brightness, and kelvin.

    >>> import lifx
    >>> hsbk = lifx.lan.light.HSBK()
    >>> hsbk.hue = 32369
    >>> hsbk.saturation = 19660
    >>> hsbk.brightness = 22281
    >>> hsbk.kelvin = 3500
    >>> hsbk.rgb
    (61, 87, 86)
    >>> hsbk.rgb = (30, 60, 90)
    >>> hsbk.hue
    38228
    >>> hsbk.saturation
    43690
    >>> hsbk.brightness
    23039
    """

    _fields_ = [
        ("hue", c_uint16),
        ("saturation", c_uint16),
        ("brightness", c_uint16),
        ("kelvin", c_uint16),
    ]

    @property
    def rgb(self):
        """Return the color as an (R, G, B) tuple (values 0-256)."""
        (r, g, b) = colorsys.hsv_to_rgb(
            self.hue / 65535, self.saturation / 65535, self.brightness / 65535
        )
        return int(round(r * 256)), int(round(g * 256)), int(round(b * 256))

    @rgb.setter
    def rgb(self, rgb):
        """Set the color from an (R, G, B) tuple (values 0-256)."""
        (r, g, b) = rgb
        (h, s, v) = colorsys.rgb_to_hsv(r / 256, g / 256, b / 256)
        self.hue = int(h * 65535)
        self.saturation = int(s * 65535)
        self.brightness = int(v * 65535)

    def __str__(self):
        return "hue: {}, saturation: {}, brightness: {}, kelvin: {}".format(
            self.hue, self.saturation, self.brightness, self.kelvin
        )


class Color(Union):
    """Base union providing human-scale accessors for an HSBK color field."""

    @property
    def kelvin(self):
        """The color temperature in kelvin."""
        return self.field.color.kelvin

    @kelvin.setter
    def kelvin(self, value):
        """Set the color temperature in kelvin."""
        self.field.color.kelvin = value

    @property
    def hue(self):
        """The hue angle in degrees (0–360)."""
        return round((self.field.color.hue / 65535) * 360)

    @hue.setter
    def hue(self, value):
        """Set the hue from a degree value (0–360)."""
        self.field.color.hue = round(value / 360 * 65535)

    @property
    def saturation(self):
        """The saturation as a percentage (0–100)."""
        return round((self.field.color.saturation / 65535) * 100)

    @saturation.setter
    def saturation(self, value):
        """Set the saturation from a percentage value (0–100)."""
        self.field.color.saturation = round(value / 100 * 65535)

    @property
    def brightness(self):
        """The brightness as a percentage (0–100)."""
        return round((self.field.color.brightness / 65535) * 100)

    @brightness.setter
    def brightness(self, value):
        """Set the brightness from a percentage value (0–100)."""
        self.field.color.brightness = round(value / 100 * 65535)

    @property
    def rgb(self):
        """The color as an (R, G, B) tuple."""
        return self.field.color.rgb

    @rgb.setter
    def rgb(self, triple):
        """Set the color from an (R, G, B) tuple."""
        self.field.color.rgb = triple

    def __str__(self):
        return "hue: {}, saturation: {}, brightness: {}, kelvin: {}, rgb: {}".format(
            self.hue, self.saturation, self.brightness, self.kelvin, self.rgb
        )


class Get(LittleEndianStructure):
    """A LIFX Get request for the current light state, with no payload."""

    _fields_: list = []

    state = "get_light"

    def __str__(self):
        return "Get"


class _State(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("color", HSBK),
        ("", c_uint16),
        ("power", c_uint16),
        ("label", c_uint8 * 32),
        ("", c_uint64),
    ]


class State(Color):
    """
    A LIFX StateLight response containing color, power, and label fields.

    >>> import lifx
    >>> body = lifx.lan.light.State()
    >>> body.rgb = (0, 255, 0)
    >>> body.field.color.rgb
    (0, 255, 0)
    >>> body.kelvin = 3500
    >>> body.field.color.kelvin
    3500
    >>> body.label = "pippo"
    >>> body.label
    'pippo'
    >>> body.power = 11
    >>> body.field.power
    11
    >>> body.hue
    120
    >>> body.field.color.hue
    21845
    >>> body.saturation
    100
    >>> body.field.color.saturation
    65535
    >>> body.brightness
    100
    >>> body.field.color.brightness
    65279
    >>> body.hue = 240
    >>> body.hue
    240
    >>> body.saturation = 100
    >>> body.saturation
    100
    >>> body.brightness = 100
    >>> body.brightness
    100
    """

    state = "state_light"

    _fields_ = [("field", _State), ("bytes", c_uint8 * 52)]

    @property
    def power(self):
        """The power level of the light (0 = off, 65535 = on)."""
        return self.field.power

    @power.setter
    def power(self, value):
        """Set the power level of the light."""
        self.field.power = value

    @property
    def label(self):
        """The human-readable label of the light, up to 32 UTF-8 characters."""
        lbl = ""
        for i in range(0, 32):
            c = chr(self.field.label[i])
            if c == chr(0):
                break
            else:
                lbl += c
        return lbl

    @label.setter
    def label(self, value):
        """Set the light label from a UTF-8 string."""
        for i, byte in enumerate(bytes(value, "utf-8")):
            self.field.label[i] = byte

    def __str__(self):
        color = super(State, self).__str__()
        return "State {{power: {}, {}, label: {}}}".format(
            self.power, color, self.label
        )


class _SetColor(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("", c_uint8),
        ("color", HSBK),
        ("duration", c_uint32),
    ]


class SetColor(Color):
    """
    A LIFX SetColor command containing color and transition duration fields.

    >>> import lifx
    >>> body = lifx.lan.light.SetColor()
    >>> body.rgb = (0, 255, 0)
    >>> body.field.color.rgb
    (0, 255, 0)
    >>> body.kelvin = 3500
    >>> body.field.color.kelvin
    3500
    >>> body.duration = 0xAABBCCDD
    >>> body.field.duration
    2864434397
    """

    state = "set_color_light"

    _fields_ = [("field", _SetColor), ("bytes", c_uint8 * 13)]

    @property
    def duration(self):
        """The color transition duration in milliseconds."""
        return self.field.duration

    @duration.setter
    def duration(self, value):
        """Set the color transition duration in milliseconds."""
        self.field.duration = value

    def __str__(self):
        color = super(SetColor, self).__str__()
        return "SetColor {{{}, duration: {}}}".format(color, self.duration)


class _SetWaveform(LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ("", c_uint8),
        ("transient", c_uint8),
        ("color", HSBK),
        ("period", c_uint32),
        ("cycles", c_float),
        ("skew_ratio", c_int16),
        ("waveform", c_uint8),
    ]


class SetWaveform(Color):
    """
    A LIFX SetWaveform command for animating a light with a periodic waveform.

    >>> import lifx
    >>> body = lifx.lan.light.SetWaveform()
    >>> body.rgb = (0, 255, 0)
    >>> body.field.color.rgb
    (0, 255, 0)
    >>> body.kelvin = 3500
    >>> body.field.color.kelvin
    3500
    >>> body.waveform = "triangle"
    >>> body.field.waveform
    3
    >>> body.waveform == body.Waveform.triangle
    True
    >>> body.skew_ratio = 0
    >>> body.field.skew_ratio
    -32768
    >>> body.skew_ratio = 0.5
    >>> body.field.skew_ratio
    0
    >>> body.skew_ratio = 1
    >>> body.field.skew_ratio
    32767
    >>> body.transient = True
    >>> body.field.transient
    1
    >>> body.transient = False
    >>> body.field.transient
    0
    """

    state = "set_waveform_light"

    class Waveform(IntEnum):
        """Enumeration of supported LIFX waveform types."""

        saw = (0,)
        sine = (1,)
        halfsine = (2,)
        triangle = (3,)
        pulse = (4,)

    _fields_ = [("field", _SetWaveform), ("bytes", c_uint8 * 21)]

    @property
    def transient(self):
        """Whether the color returns to its original value after the waveform."""
        return self.field.transient

    @transient.setter
    def transient(self, value):
        """Set whether the color reverts after the waveform completes."""
        self.field.transient = value

    @property
    def period(self):
        """The duration of one waveform cycle in milliseconds."""
        return self.field.period

    @period.setter
    def period(self, value):
        """Set the duration of one waveform cycle in milliseconds."""
        self.field.period = value

    @property
    def cycles(self):
        """The number of waveform cycles to run."""
        return self.field.cycles

    @cycles.setter
    def cycles(self, value):
        """Set the number of waveform cycles to run."""
        self.field.cycles = value

    @property
    def skew_ratio(self):
        """The skew ratio controlling waveform asymmetry (0.0 to 1.0)."""
        return round(self.field.skew_ratio / 65535) + 32768

    @skew_ratio.setter
    def skew_ratio(self, value):
        """Set the skew ratio from a float in the range 0.0 to 1.0."""
        self.field.skew_ratio = round(value * 65535) - 32768

    @property
    def waveform(self):
        """The waveform type as a Waveform enum value."""
        return self.Waveform(self.field.waveform)

    @waveform.setter
    def waveform(self, value):
        """Set the waveform type by name string."""
        value = getattr(self.Waveform, value)
        self.field.waveform = self.Waveform(value)

    def __str__(self):
        color = super(SetWaveform, self).__str__()
        return "SetWaveform {{{}, transient: {}, period: {}, cycles: {}, skew_ratio {}, waveform {}}}".format(
            color,
            self.transient,
            self.period,
            self.cycles,
            self.skew_ratio,
            self.waveform,
        )


class Power:
    """Mixin providing a level property for power-related message classes."""

    @property
    def level(self):
        """The power level (0 = off, 65535 = on)."""
        return self.field.level

    @level.setter
    def level(self, value):
        """Set the power level."""
        self.field.level = value

    def __str__(self):
        return "level: {}".format(self.level)


class GetPower(LittleEndianStructure):
    """A LIFX GetPower request message with no payload."""

    _fields_: list = []

    state = "get_power_light"

    def __str__(self):
        return "GetPower"


class _SetPower(LittleEndianStructure):

    _pack_ = 1
    _fields_ = [
        ("level", c_uint16),
    ]


class SetPower(Power, Union):
    """A LIFX SetPower command message to turn the light on or off."""

    ON = 65535
    OFF = 0
    state = "set_power_light"

    _fields_ = [("field", _SetPower), ("bytes", c_uint8 * 52)]

    def __str__(self):
        level = super(SetPower, self).__str__()
        return "SetPower {{{}}}".format(level)


class _StatePower(LittleEndianStructure):

    _pack_ = 1
    _fields_ = [
        ("level", c_uint16),
        ("port", c_uint32),
    ]


class StatePower(Power, Union):
    """A LIFX StatePower response message reporting the current power level."""

    ON = 65535
    OFF = 0
    state = "state_power_light"

    _fields_ = [("field", _StatePower), ("bytes", c_uint8 * 52)]

    def __str__(self):
        level = super(StatePower, self).__str__()
        return "StatePower {{{}}}".format(level)


class State_Factory(object):
    """Factory for creating LIFX light state instances from a name and value dict."""

    @staticmethod
    def make(state: str, fields_values: dict) -> TUnion[
        "lifx.lan.light.SetColor",
        "lifx.lan.light.SetWaveform",
        "lifx.lan.light.SetPower",
        "lifx.lan.light.GetPower",
        "lifx.lan.light.GetService",
        "lifx.lan.light.StateService",
        "lifx.lan.light.State",
    ]:
        """
        Make a Lifx Msg given a dictionary of values

        :param state: a string representation of a Lifx State
        :param fields_values: a dictionary of values for the State

        >>> import lifx
        >>> factory = lifx.lan.light.State_Factory()
        >>> state = factory.make("SetColor", {"rgb": (20, 20, 20), "kelvin": 3500, "duration": 1024})
        >>> state.rgb
        (20, 20, 20)
        >>> state.kelvin
        3500
        >>> state.duration
        1024
        >>> state = factory.make("SetColor", {"hue": 360, "saturation": 89, "brightness": 89, "kelvin": 3500, "duration": 1024})
        >>> state.hue
        360
        >>> state.saturation
        89
        >>> state.brightness
        89
        """
        thismodule = sys.modules[__name__]
        instance = getattr(thismodule, state)()
        for key, value in fields_values.items():
            setattr(instance, key, value)
        return instance


class Description_Factory(object):
    """Factory for extracting a (class-name, field-values) description from a state instance."""

    @staticmethod
    def make(
        state: TUnion[
            "lifx.lan.light.SetColor",
            "lifx.lan.light.SetWaveform",
            "lifx.lan.light.SetPower",
            "lifx.lan.light.GetPower",
            "lifx.lan.light.GetService",
            "lifx.lan.light.StateService",
            "lifx.lan.light.State",
        ]
    ) -> tuple[str, dict]:
        """
        :param state: a list of bytes to be interpreted as a state
        :return a dict

        >>> import lifx
        >>> factory = lifx.lan.light.Description_Factory()
        >>> color = lifx.lan.light.SetColor()
        >>> s = factory.make(color)
        >>> s[1]['rgb'] = (0, 0, 0)
        >>> s[1]['kelvin'] = 0
        >>> s[1]['duration'] = 0
        >>> s[1]['hue'] = 0
        >>> s[1]['brightness'] = 0
        >>> s[1]['saturation'] = 0
        """
        description = {}
        fields = set(
            [
                name
                for name, _ in inspect.getmembers(
                    state.__class__, inspect.isdatadescriptor
                )
            ]
        ) - set(
            [
                "bytes",
                "field",
                "__weakref__",
                "_b_base_",
                "_b_needsfree_",
                "_objects",
            ]
        )
        for name in fields:
            field = state.__getattribute__(name)
            if isinstance(field, IntEnum):
                description[name] = field.name
            else:
                description[name] = field
        return state.__class__.__name__, description
