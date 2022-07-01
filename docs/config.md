# Configuration

First, let's create a copy of the default configuration:
```bash
cd src
cp config_default.json config.json
```

Now, open `config.json` in `nano` or any other texteditor. You will be greeted by the default config:

```json
{
	"feeder": {
		"enabled": false,
		"apikey": "",
		"endpoints": []
	},
	"radio": {
		"device_id": 0,
		"gain": "automatic",
		"timeout": 315,
		"multimon-version": "1.1.9"
	},
	"webserver": {
		"enabled": false,
		"hostname": "",
		"port": 8112,
		"messages": 250
	}
}
```

## Feeder

The `feeder` entry controls feeding your received information to online-services of your liking. By default, this feature is disabled.

###### enabled

Whether feeding should be done at all.
In the case feeding is enabled and no API key is provided, feeding to **112Centraal** will be disabled while the other feeds will continue to work.
[`true`|`false`]

###### apikey

API key for **112Centraal** specifically. To support this project, you can apply to become a feeder and receive some extra benefits of **Open112**.

Please refer to the <a href="/docs/feeding.md">Feeding</a> manual to learn more about feeding **112Centraal** or feeding to custom servers.

###### endpoints

A JSON array of custom url's to feed data to.
Theoretically this list can be infinite, but be aware that a lot of endpoints can use more hardware resources / bandwidth.

**Example:**
```json
{
	"feeder": {
		"enabled": true,
		"apikey": "YourKeyHere",
		"endpoints": [
			"https://example.com/custom/endpoint",
			"https://jkctech.nl/feed"
		]
	},
...
```

## Radio

The `radio` entry takes information about your SDR and how to demodulate the incoming FLEX messages.

###### device_id

If you have more than 1 SDR in your device, you can target a specific SDR.
See available SDR id's by running `rtl_test`.

###### gain

Controls the gain for the receiver. Valid values can be observed by running `rtl_test`.
Because the gain can be either a number or `automatic`, please input this value as a string.

###### timeout

SDR devices can freeze or drop out. If no incoming messages have been received in this amount of seconds, the software will restart in an attempt to resolve the issue. Since `MKOB Den Bosch` sends out a ping every 5 minutes sharp, we can use this in our advantage.

###### multimon-version

In the case you specifically want to run Multimon-NG on `1.1.8`, the decoding has to be adapted because of formatting changes between `1.1.8` and `1.1.9`.
Please try to avoid running on 1.1.8 where you can!

**Example:**
```json
...
	"radio": {
		"device_id": 1,
		"gain": "49.6",
		"timeout": 315,
		"multimon-version": "1.1.9"
	},
...
```

## Webserver

Open112 has an included mini "webserver" that can be displayed on a screen and shows live incoming data from your receiver.

**WARNING:** The used Python module for the webserver is not meant for production use and should **NOT** be open to the public.

**Use at your own risk!**

###### enabled

Whether the webserver should be enabled or not.
[`true`|`false`]

###### hostname

Hostname to bind to. If you do not know what this is and do not require a specific ip or hostname, you should probably leave this empty.

###### port

Webserver port. Default is `8112` because I am THAT good at being original :)

###### messages

The amount of messages the webserver should keep in memory. More messages take more memory obviously...

**Example:**
```json
...
	"webserver": {
		"enabled": true,
		"hostname": "",
		"port": 8112,
		"messages": 420
	}
}
```
