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

- [ ] Test the G-Helper ASUS battery query on the ROG Strix Go 2.4.
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

- [ ] Implement Linux HID code that can reliably read the battery percentage.
- [ ] Discover the device using VID/PID or a stable udev path instead of `/dev/hidrawN`.
- [ ] Add freedesktop notification support for the low-battery threshold.
- [ ] Add a separate notification for critical battery level.
- [ ] Evaluate charging started/finished notifications once charging state detection is available.
- [ ] Design background operation independently of the desktop environment/window manager.
- [ ] Configure the user service / udev permissions.
- [ ] Automatically rediscover the device when the dongle is reconnected.

## 🚫 Out of Scope

- [x] EQ control will not be included in the project. It can be handled through PipeWire/EasyEffects.
- [x] An Armoury Crate clone will not be developed.
- [x] Unnecessary ASUS device controls are not a priority until battery reading is solved.

## Next Session

1. Carefully test the G-Helper `[reportId, 0x12, 0x01]` query against the ROG Strix Go 2.4's actual vendor report IDs.
2. If a report responds, record the raw response bytes.
3. Compare the response at different battery and charging states.
4. Add the findings to `research/rog-strix-go-2-4-linux-research.md`.
5. Once the battery field is verified, proceed to the actual Linux battery reader implementation.
