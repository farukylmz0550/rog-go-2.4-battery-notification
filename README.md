# ROG Go 2.4 Battery Notification

A project focused on monitoring the battery level of the ASUS ROG Strix Go 2.4 on Linux.

> ⚠️ **Early development stage**
>
> The project can now successfully query the headset battery through the Linux `hidraw` interface. Battery percentage validation against a changing physical battery level is still pending.

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

**Research / Reverse Engineering / Initial Linux C Prototype**

The battery query and Linux HID transport are working in a prototype. The next major validation step is confirming that the reported percentage changes with the physical battery level before building the notification layer.
