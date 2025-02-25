# Primare Mediaplayer Component
This is a Custom Component for Home-Assistant (https://home-assistant.io).

You can read and control a Primare reciever, this is working in combination with a USB to Serial converter

## Installation

### Manual
- Copy directory `primareusb` to your `<config dir>/custom_components` directory.
- Copy directory `primare_preamp` to your `<config dir>/deps/lib/python3.10/site-packages` or '<config dir>/lib/python3.10/site-packages/' directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

media_player: 
  - platform: primareusb
    serial_port: /dev/ttyUSB0
```

Configuration variables:

- **serial_port** (*Required*): The USB port on which the USB to Serial can be reached.
- **sources** (*Required*): This is depending on your own set-up.
- **name** (*Optional*): Name of the device. (default = 'Primare Preamp')
- **min_volume** (*Optional*): Minimal volume of the reciever, will also appear on the volume slider from 0-100% (default = '79')
- **max_volume** (*Optional*): Maximal volume of the reciever, will also appear on the volume slider from 0-100%  (default = '0')
