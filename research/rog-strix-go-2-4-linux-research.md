# ROG Strix Go 2.4 Linux Research

## Goal

Primary goal: read the ROG Strix Go 2.4 battery percentage on Linux and show low-battery desktop notifications through the freedesktop notification interface, so the app is desktop-environment/window-manager independent.

Secondary features such as microphone mute handling, charging notifications, and ASUS-specific controls are optional.

## Device identification

- Product: ASUS ROG STRIX Go 2.4
- USB VID: `0x0B05`
- USB PID: `0x18D6`
- USB device revision observed: `37.65`
- USB speed: Full Speed
- HID interface path observed: `1-1:1.3`
- Current HID character device is typically `/dev/hidraw5`, but hidraw numbering can change after reconnect/re-enumeration.
- Therefore software must discover the device by VID/PID/name rather than rely on a fixed hidraw number.

## Linux device layout

PipeWire currently exposes:

- Sink: `ROG STRIX Go 2.4 Analog Stereo`
- Source: `ROG STRIX Go 2.4 Mono`

UPower and `/sys/class/power_supply/` do not currently expose a battery device for the headset.

## HID/input interfaces

`event18`:

`ASUS ROG STRIX Go 2.4 Consumer Control`

Supported controls:

- `KEY_MUTE`
- `KEY_VOLUMEDOWN`
- `KEY_VOLUMEUP`
- `KEY_NEXTSONG`
- `KEY_PLAYPAUSE`
- `KEY_PREVIOUSSONG`

Physical behavior observed:

- Volume up -> `KEY_VOLUMEUP`
- Volume down -> `KEY_VOLUMEDOWN`
- Microphone mute button -> `KEY_MUTE`
- Play/Pause button: 1 click -> `KEY_PLAYPAUSE`
- Play/Pause button: 2 clicks -> `KEY_NEXTSONG`
- Play/Pause button: 3 clicks -> `KEY_PREVIOUSSONG`

The physical mute button is known to be a microphone mute control. Testing showed that the microphone continued to capture audio when the physical mute button was pressed, and `wpctl get-volume` did not show a `MUTED` state. Therefore hardware-level microphone cutoff has not been demonstrated. The button definitely generates `KEY_MUTE` in Linux.

`event19`:

- Device name: `ASUS ROG STRIX Go 2.4`
- `BTN_0`
- `ABS_MISC`, range `0..13`
- No meaningful event changes observed during tested normal controls.

`event20`:

- Device name: `ASUS ROG STRIX Go 2.4`
- `ABS_MISC`, range `0..65535`
- No meaningful event changes observed during tested normal controls.

These are currently unknown interfaces. They have not been shown to be microphone audio; the actual microphone audio is the PipeWire/ALSA source above.

## HID report descriptor

The HID report descriptor length is 426 bytes.

Important report IDs and structure:

### Report 0x01

Consumer Control input report.

The first three relevant bits are:

- bit 0 -> Volume Up (`0xE9`)
- bit 1 -> Volume Down (`0xEA`)
- bit 2 -> Mute (`0xE2`)

The descriptor also contains previous/play-next usages (`0xB6`, `0xCD`, `0xB5`). Multi-click behavior was observed at the Linux input layer/device behavior level.

### Report 0x64

Vendor-defined input report on usage page `0xFFC0`.

Structure includes:

- 4-bit field
- 4-bit field

No live report observed yet.

### Report 0x65

Vendor-defined input report on usage page `0xFFC0`.

Structure includes:

- 3-bit field
- 5-bit field

No live report observed yet.

### Report 0xFF

There is both an Input report and a Feature report.

Feature structure:

- 1 byte field
- 62 one-bit fields

A `GET_FEATURE` request succeeds.

Observed response:

```text
ff 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

Observed length: 27 bytes.

The same response was obtained in 10 consecutive reads.

The response was also unchanged before and after connecting/disconnecting the headset's USB-C charging cable during the charging test. Therefore the currently observed `0xFF` response is not a useful direct battery indication.

Important: the meaning of the `0x01` byte after the Report ID is unknown and must not be assumed.

### Report 0x90

Vendor-defined input/output report.

Input structure:

- 1 byte field
- 1 byte field
- 2 byte field
- 10 byte field

Output structure is the same.

No spontaneous `0x90` input report was observed during passive listening or normal tested controls.

### Report 0xC4

Vendor-defined input/output report.

Input structure:

- 1 byte field
- 1 byte field
- 2 byte field
- 59 byte field

Output structure is the same.

No spontaneous `0xC4` input report was observed during passive listening or normal tested controls.

### Report 0xE2

Input-only report with:

- 1 byte field
- 62 one-bit fields

No spontaneous `0xE2` input report was observed during passive listening or normal tested controls.

## Passive HID testing

`hid-recorder /dev/hidraw5` successfully showed the descriptor and standard Consumer Control events.

Example observed raw report:

```text
01 00 02 00 00
01 00 00 00 00
```

This corresponds to a Volume Down press/release according to the descriptor.

A 30-second passive read from `/dev/hidraw5` produced no spontaneous vendor Input reports (`0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`).

## USB monitor

`usbmon` kernel module can be loaded, but reading debugfs usbmon streams is blocked by kernel lockdown.

Observed:

```text
Lockdown: cat: debugfs access is restricted
```

Lockdown state:

```text
none [integrity] confidentiality
```

Therefore usbmon is currently not being used for protocol capture.

## Current battery investigation status

Standard Linux battery interfaces:

- `/sys/class/power_supply/` -> no battery device
- `upower -e` -> only `DisplayDevice`
- `upower` search for ASUS/ROG/18d6 -> no headset battery

HID:

- `0xFF` Feature report is readable but remained constant across the charging-state test.
- `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2` have not yet produced a useful spontaneous battery value.

Therefore the actual battery percentage source remains unknown.

## Useful existing code/tooling

A local HID explorer script has been used at `~/Desktop/test.py`.

Current explorer behavior:

- Detects/uses the ROG HID interface
- Reads Feature Report `0xFF`
- Listens for Input Reports
- Can print Report IDs `0x01`, `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`

Note: automatic discovery must be based on actual VID/PID/name because hidraw numbering can change.

## Next battery-focused research steps

1. Parse the vendor reports more completely and map all fields.
2. Investigate `0x90` and `0xC4` output packet semantics without random writes.
3. Investigate `0xE2` and `0xFF` bitfields.
4. Search existing Linux/GitHub implementations and firmware for `0b05:18d6`, `0x90`, `0xC4`, and related identifiers.
5. If available, compare Windows/Armoury Crate USB HID traffic to identify battery queries.
6. Once battery percentage is identified, build a small desktop-independent notifier using the freedesktop notification API.

## Scope decisions

- EQ is out of scope. It can be handled separately via PipeWire/EasyEffects.
- A full Armoury Crate clone is out of scope.
- The primary feature is battery percentage + low-battery notification.
- All other device controls are optional until battery reporting is solved.
