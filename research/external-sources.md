# External Sources

This file records external sources used during the research and development of the ROG Strix Go 2.4 Linux battery support.

## G-Helper PR #5159

- **Source:** G-Helper Pull Request #5159
- **URL:** https://github.com/seerge/g-helper/pull/5159
- **Title:** Add ROG Strix Go 2.4 support
- **Repository:** `seerge/g-helper`
- **Pull request:** `#5159`
- **Purpose:** Primary external reference for the ROG Strix Go 2.4 HID battery protocol and the initial implementation details.

### Relevant findings

The pull request adds initial support for the ASUS ROG Strix Go 2.4 and identifies the device through its `MI_03` HID interface.

The relevant USB identifiers are:

```text
VID: 0x0B05
PID: 0x18D6
Interface: MI_03
Feature report length: 64 bytes
```

The implementation uses Feature Report ID `0xFF` for the battery query.

The known battery query packet is:

```text
FF 08 00 FD 04 12 F1 03 52 01
```

The packet is padded to the 64-byte Feature Report buffer size before it is sent.

The documented response has the following general form:

```text
FF 1B 05 FE 12 04 1F 14 01 03 05 XX 0E YY 12 01 00 17 25 05 20 B4 00 0A FD ...
```

For the Strix Go 2.4 implementation:

- `response[13]` contains the battery percentage.
- `0x40` at `response[13]` represents `64%`.
- `response[11]` is a status/connection-related value, but its exact charging-state meaning is not confirmed.

The pull request explicitly leaves charging detection disabled because the exact charging-state byte still needs confirmation.

### Linux porting relevance

The Windows implementation uses HID Feature Reports. On Linux, the equivalent operation should use the `hidraw` Feature Report ioctls:

- `HIDIOCSFEATURE` to send the Feature Report.
- `HIDIOCGFEATURE` to read the Feature Report response.

The battery implementation should initially focus only on reading `response[13]` and validating the reported percentage against the physical headset state. Charging detection and other device features are optional future work.

## Source attribution

The G-Helper PR is an external source and protocol reference. The Linux implementation in this repository is an independent implementation using Linux `hidraw` interfaces and is not a copy of the G-Helper Windows implementation.
