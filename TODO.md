# TODO

Research and development task list.

## ✅ Completed

- [x] ROG Strix Go 2.4 USB HID device identified.
- [x] USB VID/PID identified: `0x0B05:0x18D6`.
- [x] Confirmed that battery information is not available through standard Linux `UPower` / `/sys/class/power_supply/`.
- [x] Relevant HID interface identified: `1-1:1.3` / `MI_03`.
- [x] Access to the device established through `hidraw`.
- [x] HID report descriptor extracted and important report IDs identified: `0x01`, `0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`, `0xFF`.
- [x] Consumer Control report analyzed and volume/mute/media controls verified.
- [x] `GET_FEATURE` successfully performed for HID Feature Report `0xFF`.
- [x] Confirmed that the observed response from HID Feature Report `0xFF` did not change depending on whether the charging cable was connected.
- [x] Observed that vendor reports (`0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`) did not spontaneously produce meaningful data during passive HID monitoring so far.
- [x] Confirmed that `usbmon` access is blocked by kernel lockdown.
- [x] Found the generic ASUS HID battery query protocol in the G-Helper source code.
- [x] Identified the candidate query structure used by G-Helper: `[reportId, 0x12, 0x01]`.
- [x] Confirmed that the generic ASUS protocol uses `response[6]` for battery percentage and `response[9]` for charging state.
- [x] Confirmed that no direct `0x0B05:0x18D6` / ROG Strix Go 2.4 battery implementation was found in the G-Helper source. Therefore, the protocol is not assumed to work for the headset.
- [x] Verified the headset-specific query from G-Helper PR #5159 (`FF 08 00 FD 04 12 F1 03 52 01`) on the dongle MI_03 interface: accepted, answered with the `FF 1B ...` response type.
- [x] Implemented and physically tested the modular C battery reader (monitor mode: ~1 s disconnect detection, automatic rediscovery, `uaccess` udev rule installed and verified).
- [x] Determined that `0B05:18D7` ("ROG STRIX Go 2.4 Headset Battery Charger") is the headset itself enumerated when its USB-C charging cable is connected to the PC; it disappears when the cable is unplugged (observation during the 2026-09-14 sessions).

## ❌ Unresolved / Not Yet Solved

- [ ] Battery percentage could not be read directly from HID Feature Report `0xFF`.
- [ ] The meaning of report `0x64` has not been determined.
- [ ] The meaning of report `0x65` has not been determined.
- [ ] The meaning of report `0x90` has not been determined.
- [ ] The meaning of report `0xC4` has not been determined.
- [ ] The meaning of report `0xE2` has not been determined.
- [ ] The meaning of the `ABS_MISC` fields on `event19` and `event20` has not been determined.
- [ ] No reliable battery percentage has been obtained from any HID report so far.
- [ ] No reliable charging state has been obtained from any HID report so far.
- [ ] The actual HID battery query used by Windows / Armoury Crate has not yet been captured.

## 🔬 Battery / HID Discovery

- [x] Test the G-Helper ASUS battery query on the ROG Strix Go 2.4. *(headset-specific variant accepted by the dongle MI_03 interface, `0x1B` response)*
- [ ] Carefully investigate whether `[reportId, 0x12, 0x01]` is accepted on candidate report IDs (`0x90`, `0xC4`, `0xFF`).
- [ ] If a query produces a response, record the response structure and verify fields such as `response[6]` / `response[9]`.
- [ ] Verify the suspected battery field at different battery levels.
- [ ] Compare the same field while charging and while not charging.
- [ ] Investigate in more detail why `HIDIOCGFEATURE` returned `ff 01...`-style data when queried against non-Feature report IDs.
- [ ] Document the `Broken pipe` behavior observed with `HIDIOCGINPUT` and investigate alternative methods.
- [ ] Analyze vendor input report `0x64`.
- [ ] Analyze vendor input report `0x65`.
- [ ] Analyze input/output report `0x90`.
- [ ] Analyze input/output report `0xC4`.
- [ ] Analyze input report `0xE2`.
- [ ] Analyze the fields of the `0xFF` Feature/Input report.
- [ ] Compare HID behavior with the charging cable connected and disconnected.
- [ ] Compare the headset powered on and powered off.
- [ ] Compare the dongle connected and disconnected.
- [ ] Perform controlled state tests on `event19` and `event20`.

## 🔎 Existing Source Code Research

- [x] Inspected the generic `ReadBattery()` approach in G-Helper `AsusKeyboard.cs`.
- [x] Inspected `HasBattery()` implementations for ASUS models supported by G-Helper.
- [ ] Verify whether G-Helper issue/PR history contains a device-specific battery protocol for the ROG Strix Go 2.4 (`18D6`).
- [ ] Search GitHub for other implementations matching `0B05:18D6`, `18D6`, `0x90`, `0xC4`, and `0x12 0x01`.

## 🧩 Firmware / Windows Research

- [ ] Statistically analyze the ASUS `S54WL_Update_V3763` firmware package.
- [ ] Search the firmware/update executable for strings related to `0b05`, `18d6`, HID report IDs, and battery functionality.
- [ ] Investigate the protocol used by Armoury Crate / Armoury II to communicate with the device.
- [ ] If possible, capture the actual HID traffic with Windows + USBPcap + Wireshark.
- [ ] Identify the battery query request/response pair.

## 🛠️ Application

- [x] Implemented a modular Linux C battery reader (`src/main.c`, `src/device.c`, `src/battery.c`, `src/util.c`).
- [x] Discovered the device dynamically through `libudev` (hidraw -> USB interface `bInterfaceNumber == 3` -> `idVendor 0B05` / `idProduct 18D6`) instead of a fixed `/dev/hidrawN` path.
- [x] Added a monitor mode that tolerates dongle disconnects and automatically rediscovers the device on reconnect.
- [x] Added a `--debug` mode that dumps raw SET_FEATURE/GET_FEATURE exchanges for protocol research.
- [ ] Validate that `response[13]` changes with the physical battery level. **Current observation: the value stayed at `0x40` (`64`) during discharge and charging, so byte 13 as battery percentage is unconfirmed.**
- [ ] Identify the byte that actually reports the battery percentage (note: ASUS is reported to show this headset's battery in 25% increments in Armoury Crate).
- [ ] Investigate the separate `0B05:18D7` "ROG STRIX Go 2.4 Headset Battery Charger" USB device as a possible battery/charging data source.
- [ ] Add freedesktop notification support for the low-battery threshold.
- [ ] Add a separate notification for critical battery level.
- [ ] Evaluate charging started/finished notifications once charging state detection is available.
- [ ] Design background operation independently of the desktop environment/window manager.
- [ ] Configure the user service / udev permissions. *(A `uaccess` rule is now shipped in `deploy/udev/70-rog-strix-go-2.4.rules`; system service configuration comes with the notification stage.)*
- [ ] Automatically rediscover the device when the dongle is reconnected. *(done in the monitor mode of `rog-go-battery`)*

## 🧪 Battery Validation Plan (next experiments)

Protocol will only be revised from measured data, never from assumptions.
Only the known battery query is sent to candidate interfaces; no invented
commands.

### Experiment A - charging ramp (fast signal, ~1 h)

Status as of 2026-09-14 ~23:40 (session cut short by shutdown):

- [x] Dongle battery query logged every 30 s while the headset charges via the PC USB-C port (`research/captures/2026-09-14-charging-ramp-capture.txt`; `rog-ramp2.service` user unit was logging).
- [x] `0B05:18D7` HID interfaces probed with the known battery query: feature report `0xFF` is static (`FF 01 00...`), `0xFD` is input-only, no spontaneous input reports in 20 s of passive reading. The 18D7 HID surface does not currently provide battery data.
- [x] Response type `0x01` appears transiently right after the headset is plugged in for charging / powered on; it returns to `0x1B` shortly after. Combined with the earlier 3.5 mm observation, `response[1]` appears to reflect headset association state rather than "3.5 mm mode".
- [ ] **Resume tomorrow (open question):** analyze the full ramp capture with `tools/ramp_diff.py`. So far byte 13 stayed `0x40` and bytes 11/12 drifted as a 16-bit LE pair (`0x1028` -> `0x1042`), which looks more like a cumulative counter than a battery level. Determine whether ANY byte tracks the charge level before the headset is fully charged.
- [ ] Compare the ramp capture against a capture taken while the headset is fully charged / still charging tomorrow morning, if charging continues.
- [ ] If charging finished overnight, immediately capture one `--debug` reading at full charge and compare all bytes against the pre-charge state.

### Experiment B - discharge session (definitive proof, slow)

- [ ] During normal 2.4 GHz use, log queries periodically for an extended session (the headset is reported to power itself off around 25%).
- [ ] Verify the candidate byte decreases during discharge and re-rises during the next charge.

### Experiment C - passive listening

- [ ] Passive-read the vendor input reports (`0x64`, `0x65`, `0x90`, `0xC4`, `0xE2`) while the headset is in use, to check whether battery data streams spontaneously.

## 🚫 Out of Scope

- [x] EQ control will not be included in the project. It can be handled through PipeWire/EasyEffects.
- [x] An Armoury Crate clone will not be developed.
- [x] Unnecessary ASUS device controls are not a priority until battery reading is solved.

## Next Session

1. Charge-session context for tomorrow: the dongle responses logged tonight show byte 13 constant at `0x40` while charging; bytes 11/12 drift as a 16-bit LE pair and look like an uptime counter, not a battery level. Re-run `python3 tools/ramp_diff.py research/captures/2026-09-14-charging-ramp-capture.txt` after the full charging session and after the headset has been used (discharge) to see whether any byte tracks the battery.
2. If no byte changes across charge/discharge, the dongle response likely carries only cached or non-battery data; then focus on the headset itself (`0B05:18D7`, currently probed as HID-empty) and on the Armoury Crate captures listed under Firmware / Windows Research.
3. Once the battery field is verified, proceed to the notification layer.
