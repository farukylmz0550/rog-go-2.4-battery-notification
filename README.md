# ROG Go 2.4 Battery Notification

A project focused on monitoring the battery level of the ASUS ROG Strix Go 2.4 on Linux.

> ⚠️ **Early development stage**
>
> The project can now successfully query the headset battery through the Linux `hidraw` interface with a small native C tool. Battery percentage validation against a changing physical battery level is still pending: the reported value has so far remained `64` across discharge and charging observations.

## Goal

The primary goal is:

**Read the battery percentage of the ROG Strix Go 2.4 from Linux and display a desktop notification when the battery is low.**

Notifications will work independently of the desktop environment and window manager as much as possible, using the freedesktop notification standard.

Additional features may be evaluated later.

## Current Status

- The USB device is detected by Linux.
- VID/PID: `0B05:18D6`
- The relevant HID interface is `MI_03`.
- ASUS vendor HID reports can be accessed through `hidraw`.
- Standard media controls are recognized by the Linux input system.
- UPower currently does not expose the headset as a battery device.
- No battery device for the headset is present under `/sys/class/power_supply/`.
- The headset-specific battery query has been identified from G-Helper PR #5159.
- The Linux C implementation successfully sends the known 64-byte Feature Report query and receives a response containing `response[13] = 0x40` (`64`).
- Reconnect testing confirms that the device can be rediscovered after the USB dongle is removed and reconnected.
- A different response type (`0x01`) was observed while the headset was in 3.5 mm analog mode, but its meaning has not yet been established.
- The reported `64%` value still needs validation after the physical battery level has changed.
- **Validation concern:** `response[13]` stayed at `0x40` during both discharge and charging observations. Together with reports that ASUS shows this headset's battery in 25% increments, the interpretation of byte 13 as a battery percentage is now considered unconfirmed. The protocol will only be revised based on controlled measurements, not assumptions.

## Battery Reader Tool

A Linux-native C implementation now provides the battery reader with device
discovery and connection handling:

- Dynamic device discovery through `libudev` (`hidraw` -> USB interface
  `bInterfaceNumber == 3` -> `idVendor 0B05` / `idProduct 18D6`). No fixed
  `/dev/hidrawN` path is ever assumed.
- Battery query through the Linux `hidraw` Feature Report API
  (`HIDIOCSFEATURE` / `HIDIOCGFEATURE`), following the documented protocol.
- A monitor mode that tolerates dongle disconnects and automatically
  rediscovers the device on reconnect.
- A `--debug` mode that dumps raw SET_FEATURE/GET_FEATURE exchanges to
  stderr for protocol research.

### Build

Requires a C compiler, `make`, and `libudev` development files
(`systemd-devel` on Fedora, `libudev-dev` on Debian/Ubuntu).

```sh
make
```

Or directly:

```sh
gcc -std=c11 -Wall -Wextra -O2 \
    src/main.c src/device.c src/battery.c src/util.c \
    -ludev \
    -o rog-go-battery
```

### Permissions

Hidraw nodes are root-owned by default. A udev rule is provided in
[`deploy/udev/70-rog-strix-go-2.4.rules`](deploy/udev/70-rog-strix-go-2.4.rules);
it tags the battery interface with `uaccess` so the active logged-in user
gets access without `sudo`:

```sh
sudo cp deploy/udev/70-rog-strix-go-2.4.rules /etc/udev/rules.d/
sudo udevadm control --reload && sudo udevadm trigger
```

Then unplug and replug the dongle once.

### Usage

```sh
./rog-go-battery --once   # single read, exit 0 on success
./rog-go-battery          # monitor loop: 30 s polling, auto-reconnect
./rog-go-battery --debug  # same as monitor loop, plus raw HID dumps
```

Expected output:

```text
Searching for ROG Strix Go 2.4...
Device connected: /dev/hidraw5
Battery: 64%
```

When the dongle is removed, the tool prints `Device disconnected.` and
`Waiting for device...`, then automatically rediscovers the headset when
it is plugged in again. The hidraw node number is never assumed.

## Research

Detailed reverse-engineering notes:

[`research/rog-strix-go-2-4-linux-research.md`](research/rog-strix-go-2-4-linux-research.md)

The research notes contain information about the HID descriptor, report IDs, Linux input interfaces, PipeWire status, the known battery protocol, C tests, reconnect testing, and the 3.5 mm analog mode observation.

## External References

The battery protocol used by this project was identified using G-Helper pull request #5159:

- [G-Helper PR #5159 - Add ROG Strix Go 2.4 support](https://github.com/seerge/g-helper/pull/5159)

PR #5159 documents the ROG Strix Go 2.4 Feature Report query and the battery percentage location used by the Windows implementation. This project uses that documented protocol as the basis for its Linux implementation.

Additional source notes are maintained in:

[`research/external-sources.md`](research/external-sources.md)

## Scope

### Core Features

- Read the battery percentage
- Display a low-battery notification
- Display a charging notification, if the charging protocol can be established reliably
- Display a critical-battery notification

### Optional

- Microphone mute behavior
- Additional device information
- ASUS-specific additional features

### Out of Scope

EQ and general audio processing are not core goals of this project. These can be handled separately through the Linux PipeWire/EasyEffects ecosystem.

## Status

**Working Linux C battery reader, protocol validation pending**

The battery reader, device discovery, and connection handling are implemented as a native C tool. The next major validation step is confirming that the reported percentage changes with the physical battery level before building the notification layer.
