"""
Support for interfacing with Primare receivers through RS-232.

For more details about this platform, please refer to the documentation at

"""
import logging

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    PLATFORM_SCHEMA)
from homeassistant.components.media_player.const import (
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE, SUPPORT_TURN_ON, SUPPORT_TURN_OFF,
    SUPPORT_VOLUME_STEP
)
from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("Loading Primare platform 1.0.0")

DEFAULT_NAME = 'Primare Receiver'
DEFAULT_MIN_VOLUME = 0
DEFAULT_MAX_VOLUME = 79

SUPPORT_MARANTZ = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_VOLUME_STEP 

CONF_SERIAL_PORT = 'serial_port'
CONF_MIN_VOLUME = 'min_volume'
CONF_MAX_VOLUME = 'max_volume'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SERIAL_PORT): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MIN_VOLUME, default=DEFAULT_MIN_VOLUME): int,
    vol.Optional(CONF_MAX_VOLUME, default=DEFAULT_MAX_VOLUME): int,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Primare platform."""
    from primare_preamp import PrimareReceiver
    add_devices([Primare(
        config.get(CONF_NAME),
        PrimareReceiver(config.get(CONF_SERIAL_PORT)),
        config.get(CONF_MIN_VOLUME),
        config.get(CONF_MAX_VOLUME),
    )], True)


class Primare(MediaPlayerEntity):
    """Representation of a Primare Receiver."""

    def __init__(self, name, primare_preamp, min_volume, max_volume):
        """Initialize the Primare Receiver device."""
        self._name = name
        self._primare_receiver = primare_preamp
        self._min_volume = min_volume
        self._max_volume = max_volume

        self._volume = self._state = self._mute = None

    def calc_volume(self, decibel):
        """
        Calculate the volume given the decibel.

        Return the volume (0..1).
        """
        return abs(self._min_volume - decibel) / abs(
            self._min_volume - self._max_volume)

    def calc_db(self, volume):
        """
        Calculate the decibel given the volume.

        Return the dB.
        """
        return self._min_volume + round(
            abs(self._min_volume - self._max_volume) * volume)

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    def update(self):
        """Retrieve latest state."""
        if self._primare_receiver.main_power('W', 'R') == '\x00':
            self._state = STATE_OFF
        else:
            self._state = STATE_ON

        if self._primare_receiver.main_mute('W', 'R') == '\x01':
            self._mute = False
        else:
            self._mute = True

        volume_result = self._primare_receiver.main_volume('W', 'R')
        if (volume_result != None):
            self._volume = self.calc_volume(volume_result)

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._mute

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_MARANTZ

    def turn_off(self):
        """Turn the media player off."""
        self._primare_receiver.main_power('W', '\x00')

    def turn_on(self):
        """Turn the media player on."""
        self._primare_receiver.main_power('W', '\x01')

    def volume_up(self):
        """Volume up the media player."""
        _LOGGER.debug("Clicked volume up")
        self._primare_receiver.main_volume('W', '\x01')

    def volume_down(self):
        """Volume down the media player."""
        _LOGGER.debug("Clicked volume down")
        self._primare_receiver.main_volume('W', '\xff')

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        vol_calc = '0' + str(self.calc_db(volume))
        self._primare_receiver.main_volume('W', vol_calc)
        
    def mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        _LOGGER.debug("Clicked mute")
        if mute:
            self._primare_receiver.main_mute('W', '\x01')
        else:
            self._primare_receiver.main_mute('W', '\x00')
