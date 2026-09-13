# ROG Go 2.4 Battery Notification

A project focused on monitoring the battery level of the ASUS ROG Strix Go 2.4 on Linux.

> ⚠️ **Early development stage**
>
> The current primary goal of the project is research and protocol discovery. There is no working battery percentage reader yet.

## Goal

The primary goal is:

**Read the battery percentage of the ROG Strix Go 2.4 from Linux and display a desktop notification when the battery is low.**

Notifications will work independently of the desktop environment and window manager as much as possible, using the freedesktop notification standard.

Additional features may be evaluated later.

## Current Status

- The USB device is detected by Linux.
- VID/PID: `0B05:18D6`
- A HID interface is available for the ROG Strix Go 2.4.
- ASUS vendor HID reports can be inspected through `hidraw`.
- Standard media controls are recognized by the Linux input system.
- UPower currently does not expose the headset as a battery device.
- No battery device for the headset is present under `/sys/class/power_supply/`.
- HID Feature Report `0xFF` can be read, but the current response does not appear to contain the battery level.
- The HID report containing the battery percentage is not yet known.

## Research

Detailed reverse-engineering notes:

[`research/rog-strix-go-2-4-linux-research.md`](research/rog-strix-go-2-4-linux-research.md)

The research notes contain information about the HID descriptor, report IDs, Linux input interfaces, PipeWire status, and the results of experiments performed so far.

## Scope

### Core Features

- Read the battery percentage
- Display a low-battery notification
- Display a charging notification
- Display a critical-battery notification

### Optional

- Microphone mute behavior
- Additional device information
- ASUS-specific additional features

### Out of Scope

EQ and general audio processing are not core goals of this project. These can be handled separately through the Linux PipeWire/EasyEffects ecosystem.

## Status

**Research / Reverse Engineering**

The project is currently in the research stage. The application architecture will be determined after the battery protocol has been identified.
