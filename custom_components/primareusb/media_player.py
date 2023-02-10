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
    SUPPORT_VOLUME_STEP, SUPPORT_SELECT_SOURCE, SUPPORT_SELECT_SOUND_MODE
)
from homeassistant.const import (
    CONF_NAME, STATE_OFF, STATE_ON)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

_LOGGER.debug("Loading Primare platform")

DEFAULT_NAME = 'Primare Receiver'
DEFAULT_MIN_VOLUME = 0
DEFAULT_MAX_VOLUME = 79

SUPPORT_MARANTZ = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_VOLUME_STEP | \
    SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE 

CONF_SERIAL_PORT = 'serial_port'
CONF_MIN_VOLUME = 'min_volume'
CONF_MAX_VOLUME = 'max_volume'
CONF_SOURCE_DICT = 'sources'
CONF_SOUNDMODE_DICT = 'soundmode'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SERIAL_PORT): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_MIN_VOLUME, default=DEFAULT_MIN_VOLUME): int,
    vol.Optional(CONF_MAX_VOLUME, default=DEFAULT_MAX_VOLUME): int,
    vol.Optional(CONF_SOURCE_DICT, default={}): {cv.string: cv.string},
    vol.Optional(CONF_SOUNDMODE_DICT, default={}): {cv.string: cv.string},
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Primare platform."""
    from primare_receiver import PrimareReceiver
    add_devices([Primare(
        config.get(CONF_NAME),
        PrimareReceiver(config.get(CONF_SERIAL_PORT)),
        config.get(CONF_MIN_VOLUME),
        config.get(CONF_MAX_VOLUME),
        config.get(CONF_SOURCE_DICT),
        config.get(CONF_SOUNDMODE_DICT)
    )], True)


class Primare(MediaPlayerEntity):
    """Representation of a Primare Receiver."""

    def __init__(self, name, primare_receiver, min_volume, max_volume,
                 source_dict, sound_mode_dict):
        """Initialize the Primare Receiver device."""
        self._name = name
        self._primare_receiver = primare_receiver
        self._min_volume = min_volume
        self._max_volume = max_volume
        self._source_dict = source_dict
        self._sound_mode_dict = sound_mode_dict
        self._reverse_mapping = {value: key for key, value in
                                 self._source_dict.items()}
        self._reverse_mapping_sound_mode = {value: "0{}".format(key) for key, value in
                                 self._sound_mode_dict.items()}

        self._volume = self._state = self._mute = self._source = None

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
            
        self._source = self._source_dict.get(
            self._primare_receiver.main_source('W', 'R'))
        self._sound_mode = self._sound_mode_dict.get(
            self._primare_receiver.main_sound_mode('W', 'R'))

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
        self._primare_receiver.main_power('W', '3')

    def turn_on(self):
        """Turn the media player on."""
        self._primare_receiver.main_power('W', '2')

    def volume_up(self):
        """Volume up the media player."""
        self._primare_receiver.main_volume('W', '1')

    def volume_down(self):
        """Volume down the media player."""
        self._primare_receiver.main_volume('W', '2')

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        vol_calc = '0' + str(self.calc_db(volume))
        self._primare_receiver.main_volume('W', vol_calc)

    def select_source(self, source):
        """Select input source."""
        self._primare_receiver.main_source('W', self._reverse_mapping.get(source))

    def select_sound_mode(self, sound_mode):
        """Select sound mode."""
        self._primare_receiver.main_sound_mode('W', self._reverse_mapping_sound_mode.get(sound_mode))
        
    def mute_volume(self, mute):
        """Mute (true) or unmute (false) media player."""
        if mute:
            self._primare_receiver.main_mute('W', '\x01')
        else:
            self._primare_receiver.main_mute('W', '\x00')
            
    @property
    def source(self):
        """Name of the current input source."""
        return self._source

    @property
    def sound_mode(self):
        """Name of the current sound_mode."""
        return self._sound_mode

    @property
    def source_list(self):
        """List of available input sources."""
        return sorted(list(self._reverse_mapping.keys()))

    @property
    def sound_mode_list(self):
        """List of available sound_modes."""
        return sorted(list(self._reverse_mapping_sound_mode.keys()))
