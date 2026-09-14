# ROG Strix Go 2.4 Linux Research

## Goal

Primary goal: read the ROG Strix Go 2.4 battery percentage on Linux and show low-battery desktop notifications through the freedesktop notification interface, so the app is desktop-environment/window-manager independent.

Secondary features such as microphone mute handling, charging notifications, and ASUS-specific controls are optional.

## References

- G-Helper PR #5159: [Add ROG Strix Go 2.4 support](https://github.com/seerge/g-helper/pull/5159)
  - Used as the primary reference for the known ROG Strix Go 2.4 HID battery protocol and implementation details.

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

The same response was obtained in 10 consecutive reads. The response was also unchanged before and after connecting/disconnecting the headset's USB-C charging cable during the charging test. Therefore the currently observed `0xFF` response is not a useful direct battery indication.

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

Earlier HID testing showed:

- `0xFF` Feature report is readable but remained constant across the charging-state test.
- `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2` did not produce a useful spontaneous battery value.

The battery protocol was subsequently identified from G-Helper PR #5159.

## Known ROG Strix Go 2.4 battery protocol

G-Helper PR #5159 adds initial ROG Strix Go 2.4 support and documents the headset-specific Feature Report query.

The device is identified by:

```text
VID:PID = 0x0B05:0x18D6
interface = MI_03
feature report length = 64 bytes
```

The battery query uses Feature Report ID `0xFF` and sends:

```text
FF 08 00 FD 04 12 F1 03 52 01
```

The packet is padded with zeroes to the 64-byte Feature Report buffer size.

The returned response is documented in the PR in this general form:

```text
FF 1B 05 FE 12 04 1F 14 01 03 05 XX 0E YY 12 01 00 17 25 05 20 B4 00 0A FD ...
```

For this headset implementation:

- `response[13]` = battery percentage
- `0x40` at `response[13]` represents `64%`
- the byte at `response[11]` is observed as a status/connection-related value, but its exact charging meaning is not confirmed in the PR

The PR explicitly leaves charging detection disabled because the exact charging-state byte still needs confirmation. Therefore this project should initially implement only the battery percentage and treat charging state as optional future work.

## Linux transport plan

The Windows implementation in G-Helper uses a HID feature-report transport. On Linux, the equivalent transport should use the hidraw feature-report ioctls:

- `HIDIOCSFEATURE` to send the 64-byte Feature Report containing the `0xFF` query.
- `HIDIOCGFEATURE` to read the `0xFF` Feature Report response.

`HIDIOCSOUTPUT` must not be used for this query because it is a Feature Report operation, not an Output Report operation.

The Linux implementation should:

1. Discover the headset by VID/PID and the relevant `MI_03` HID interface instead of assuming a fixed `/dev/hidrawN` path.
2. Open the corresponding hidraw device.
3. Build a 64-byte buffer beginning with the known query bytes.
4. Send it using `HIDIOCSFEATURE`.
5. Read the `0xFF` Feature Report using `HIDIOCGFEATURE`.
6. Parse `response[13]` as the battery percentage.
7. Validate the result against the physical headset battery state before treating it as reliable.

## Successful Linux C test

The low-level C implementation successfully performed the known battery query through Linux `hidraw` and `libudev`.

Successful output in 2.4 GHz mode:

```text
Device: /dev/hidraw5
VID:PID 0B05:18D6
Interface: MI_03

HIDIOCSFEATURE result: 64
GET_FEATURE:
FF 1B 05 FE 12 04 1F 14 01 03 05 F9 0D 40 15 01 01 17 25 05 20 B4 00 05 EA ...

Battery: 64%
```

A reconnect test was also completed successfully:

1. Dongle connected -> device found and battery reported as `64%`.
2. Dongle removed -> `ROG Strix Go 2.4 not found`.
3. Dongle reconnected -> device found again and battery reported as `64%`.

This confirms that the current C discovery code does not depend on a permanently assigned `/dev/hidraw5` path.

## 3.5 mm analog mode observation

The headset was then switched from 2.4 GHz wireless operation to 3.5 mm analog jack mode while the USB dongle remained available to Linux.

The same battery query produced a different response type:

```text
FF 01 00 FE 12 04 1F 14 01 03 05 DE 0D 40 15 01 01 17 25 05 20 B4 00 05 EA ...
```

Compared with the 2.4 GHz response:

```text
FF 1B 05 FE 12 04 1F 14 01 03 05 DE 0D 40 15 01 01 17 25 05 20 B4 00 05 EA ...
```

Observations:

- The response type changed from `0x1B` to `0x01`.
- `response[11]` was `0xDE` in this observation.
- `response[13]` remained `0x40`, corresponding to `64%`.
- The C parser currently reports the `0x01` response as `Unexpected response type: 0x01` because it was written to accept the `0x1B` response documented by G-Helper.

Important: this does **not** establish that `0x01` is a battery response type or that it specifically represents 3.5 mm mode. It only records the observed correlation. The data after the first response bytes is very similar to the known wireless response, including the same `response[13]` value.

## Wireless stability and charging observation

During the battery validation test, the 2.4 GHz wireless connection intermittently dropped during extended use. Switching to 3.5 mm analog mode and then returning to 2.4 GHz restored the connection.

The headset was subsequently connected to USB-C charging. While charging, no similar 2.4 GHz connection drop was observed during the observed test period.

This is only an observation and does **not** establish that battery level or charging state causes the wireless disconnects. More controlled testing is required before assigning a cause.

The battery query continued to report `64%` during this period, so the observation also does not currently establish whether `response[13]` tracks the physical battery level dynamically.

## Battery percentage validation status

The battery query has been proven to work at the transport level and currently reports `64%` in repeated observations. However, the headset has not yet been observed at a known different physical battery percentage through this Linux implementation.

Therefore `response[13] = battery percentage` is currently supported by the G-Helper implementation and successful local testing, but the project should still validate that the reported percentage changes when the physical battery level changes. Repeated `64%` readings alone cannot prove that the value is stuck.

A useful validation sequence is:

```text
2.4 GHz -> read battery
3.5 mm  -> read battery
2.4 GHz -> read battery
```

and repeat after the physical battery level has changed enough to produce a measurable difference.

## Useful existing code/tooling

A local HID explorer script has been used at `~/Desktop/test.py`.

Current explorer behavior:

- Detects/uses the ROG HID interface
- Reads Feature Report `0xFF`
- Listens for Input Reports
- Can print Report IDs `0x01`, `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`

Note: automatic discovery must be based on actual VID/PID/name because hidraw numbering can change.

## Next battery-focused implementation steps

1. Continue validating `response[13]` against the actual headset battery state.
2. Investigate the meaning of the `0x01` response observed in 3.5 mm analog mode.
3. Do not infer charging state from `response[11]` until the protocol is established reliably.
4. Once battery reading is confirmed, implement periodic polling and low-battery notifications.
5. Investigate charging-state support separately only if the protocol can be established reliably.
6. Repeat controlled wireless stability tests at different battery/charging conditions.

## Scope decisions

- EQ is out of scope. It can be handled separately via PipeWire/EasyEffects.
- A full Armoury Crate clone is out of scope.
- The primary feature is battery percentage + low-battery notification.
- All other device controls are optional until battery reporting is solved.
