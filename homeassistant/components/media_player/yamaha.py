"""
homeassistant.components.media_player.yamaha
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides an interface to the Yamaha RXV Line of receivers

Configuration:

To use the Yamaha you will need to add something like the following to
your config/configuration.yaml.

media_player:
  platform: yamaha
  name: Yamaha
  url: http://192.168.1.116:80/YamahaRemoteControl/ctrl

Variables:

name
*Optional
The name of the device.

url
*Optional
The URL of the Yamaha JSON-RPC API.
Example: http://192.168.1.116:80/YamahaRemoteControl/ctrl

"""
import time
import logging

from homeassistant.const import (
    STATE_PLAYING, STATE_PAUSED, STATE_OFF, STATE_ON)

from homeassistant.components.media_player import (
    MediaPlayerDevice, SUPPORT_VOLUME_SET, SUPPORT_VOLUME_MUTE,
    SUPPORT_TURN_ON, SUPPORT_TURN_OFF
    )


_LOGGER = logging.getLogger(__name__)
REQUIREMENTS = ['rxv>=0.1.6']

MAX_VOLUME = -5.0
MIN_VOLUME = -80.5
ON_OFF_SLEEP = 2.0


def setup_platform(hass, config, add_devices, discovery_info=None):

    add_devices([
        YamahaDevice(
            config.get('name', 'Yamaha'),
            config.get('url', "")
        )
    ])

YAMAHA_DEVICE_SUPPORT =  SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
     SUPPORT_TURN_ON | SUPPORT_TURN_OFF

class YamahaDevice(MediaPlayerDevice):

    def __init__(self, name, ctrl_url):
        import rxv
        self._name = name
        self._ctrl_url = ctrl_url
        if self._ctrl_url:
            self.client = rxv.RXV(ctrl_url)
        else:
            self.client = rxv.find(timeout=2.0)[0]


    @property
    def supported_media_commands(self):
        """ Flags of media commands that are supported. """
        return YAMAHA_DEVICE_SUPPORT

    @property
    def name(self):
        """ Returns the name of the device. """
        return self.client.model_name

    @property
    def state(self):
        if self.client.on:
            return STATE_ON
        return STATE_OFF

    @property
    def volume_level(self):
        vol = self.client.volume - MIN_VOLUME
        level = vol / abs(MAX_VOLUME - MIN_VOLUME)
        return level

    def set_volume_level(self, volume):
        """ set volume level, range 0..1. """
        level = volume * abs(MAX_VOLUME - MIN_VOLUME)
        level += MIN_VOLUME
        self.client.volume = int(level)

    @property
    def is_volume_muted(self):
        """ Boolean if volume is currently muted. """
        return self.client.mute

    def mute_volume(self, mute):
        """ mute the volume. """
        self.client.mute = mute

    def turn_on(self):
        """ turn the media player on. """
        self.client.on = True
        time.sleep(ON_OFF_SLEEP)  # give it some time

    def turn_off(self):
        """ turn the media player off. """
        self.client.on = False
        time.sleep(ON_OFF_SLEEP)  # give it some time

    @property
    def media_image_url(self):
        """ Image url of current playing media. """
        return self.client.small_image_url

