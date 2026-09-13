#!/usr/bin/env python3
import argparse
import fcntl
import os
import select
import struct
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

IOC_READ = 2
IOC_WRITE = 1
HID_IOC_MAGIC = 0x48
HIDIOCGFEATURE_NR = 0x07
HIDIOCGRDESCSIZE_NR = 0x01
HIDIOCGRDESC_NR = 0x02
HID_MAX_DESCRIPTOR_SIZE = 4096


def _ioc(direction, size, type_, nr):
    return ((direction << 30) | (size << 16) | (type_ << 8) | nr)


def hid_iocgfeature(size):
    return _ioc(IOC_READ | IOC_WRITE, size, HID_IOC_MAGIC, HIDIOCGFEATURE_NR)


def hid_iocgrdesc_size():
    return _ioc(IOC_READ, 4, HID_IOC_MAGIC, HIDIOCGRDESCSIZE_NR)


def hid_iocgrdesc():
    return _ioc(IOC_READ, 4 + HID_MAX_DESCRIPTOR_SIZE, HID_IOC_MAGIC, HIDIOCGRDESC_NR)


def run_cmd(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"


def section(out, title):
    out.write("\n" + "=" * 80 + "\n")
    out.write(title + "\n")
    out.write("=" * 80 + "\n")


def dump_cmd(out, title, cmd, timeout=20):
    section(out, title)
    out.write("$ " + " ".join(cmd) + "\n\n")
    rc, stdout, stderr = run_cmd(cmd, timeout)
    if stdout:
        out.write(stdout)
        if not stdout.endswith("\n"):
            out.write("\n")
    if stderr:
        out.write("\n[stderr]\n" + stderr)
        if not stderr.endswith("\n"):
            out.write("\n")
    out.write(f"\n[exit code: {rc}]\n")


def hexdump(data, width=16):
    lines = []
    for off in range(0, len(data), width):
        chunk = data[off:off + width]
        lines.append(f"{off:04x}: " + " ".join(f"{b:02x}" for b in chunk))
    return "\n".join(lines)


def get_descriptor(fd):
    sb = bytearray(4)
    fcntl.ioctl(fd, hid_iocgrdesc_size(), sb, True)
    size = struct.unpack("I", sb)[0]
    if not 0 < size <= HID_MAX_DESCRIPTOR_SIZE:
        raise ValueError(f"invalid descriptor size: {size}")
    buf = bytearray(4 + HID_MAX_DESCRIPTOR_SIZE)
    struct.pack_into("I", buf, 0, size)
    fcntl.ioctl(fd, hid_iocgrdesc(), buf, True)
    return bytes(buf[4:4 + size])


def parse_descriptor(desc):
    reports = {}
    rid = 0
    rsize = 0
    rcount = 0
    pos = 0
    while pos < len(desc):
        prefix = desc[pos]
        pos += 1
        if prefix == 0xFE:
            if pos + 2 > len(desc):
                break
            n = desc[pos]
            pos += 2 + n
            continue
        sz_code = prefix & 3
        sz = 4 if sz_code == 3 else sz_code
        typ = (prefix >> 2) & 3
        tag = (prefix >> 4) & 0xF
        data = desc[pos:pos + sz]
        if len(data) != sz:
            break
        pos += sz
        if typ == 1:
            if tag == 7 and data:
                rsize = int.from_bytes(data, "little")
            elif tag == 8 and data:
                rid = int.from_bytes(data, "little")
            elif tag == 9 and data:
                rcount = int.from_bytes(data, "little")
        elif typ == 0:
            kind = {8: "input", 9: "output", 11: "feature"}.get(tag)
            if not kind:
                continue
            bits = rsize * rcount
            nbytes = (bits + 7) // 8
            d = reports.setdefault(rid, {"input": 0, "output": 0, "feature": 0})
            d[kind] += nbytes
    return reports


def feature_get(fd, rid, total_size):
    buf = bytearray(total_size)
    buf[0] = rid
    fcntl.ioctl(fd, hid_iocgfeature(total_size), buf, True)
    return bytes(buf)


def passive_capture(out, fd, seconds, read_size):
    section(out, f"PASSIVE HIDRAW CAPTURE ({seconds:.1f}s)")
    out.write("No SET_OUTPUT/SET_FEATURE requests are sent here.\n")
    out.write("Use the headset normally during the capture.\n\n")
    poller = select.poll()
    poller.register(fd, select.POLLIN)
    deadline = time.monotonic() + seconds
    counts = {}
    total = 0
    while time.monotonic() < deadline:
        ms = max(1, min(250, int((deadline - time.monotonic()) * 1000)))
        events = poller.poll(ms)
        for _, flags in events:
            if not (flags & select.POLLIN):
                continue
            try:
                data = os.read(fd, read_size)
            except OSError as exc:
                out.write(f"READ ERROR: {exc}\n")
                continue
            if not data:
                continue
            total += 1
            rid = data[0]
            counts[rid] = counts.get(rid, 0) + 1
            ts = datetime.now(timezone.utc).isoformat()
            out.write(f"{ts} report_id=0x{rid:02X} len={len(data)} data={data.hex(' ')}\n")
    out.write("\nCapture summary:\n")
    out.write(f"reports={total}\n")
    for rid, count in sorted(counts.items()):
        out.write(f"0x{rid:02X}: {count}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("device", nargs="?", default="/dev/hidraw5")
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output = Path(args.output or f"rog-strix-go-super-dump-{stamp}.txt")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(args.device, os.O_RDWR | os.O_NONBLOCK)
    try:
        with output.open("w", encoding="utf-8") as out:
            out.write("ROG STRIX GO 2.4 - SUPER HID/USB DUMP\n")
            out.write("=" * 80 + "\n")
            out.write(f"UTC: {datetime.now(timezone.utc).isoformat()}\n")
            out.write(f"Device: {args.device}\n")
            out.write("No undocumented Output/Feature SET commands are sent.\n")
            dump_cmd(out, "LSUSB", ["lsusb", "-d", "0b05:18d6"])
            dump_cmd(out, "LSUSB -v", ["lsusb", "-v", "-d", "0b05:18d6"], timeout=30)
            dump_cmd(out, "UDEV", ["udevadm", "info", "--query=all", "--name", args.device])
            dump_cmd(out, "UDEV PROPERTIES", ["udevadm", "info", "--query=property", "--name", args.device])
            dump_cmd(out, "KERNEL", ["uname", "-a"])
            section(out, "SYSFS")
            link = Path("/sys/class/hidraw") / Path(args.device).name
            try:
                resolved = link.resolve()
                out.write(f"class link: {link}\nresolved: {resolved}\n")
                for p in sorted(resolved.rglob("*")):
                    if p.is_file() and p.name in {"uevent", "modalias", "manufacturer", "product", "serial", "dev", "name", "phys"}:
                        try:
                            out.write(f"\n--- {p} ---\n")
                            out.write(p.read_text(errors="replace"))
                        except OSError as exc:
                            out.write(f"READ ERROR: {exc}\n")
            except OSError as exc:
                out.write(f"SYSFS ERROR: {exc}\n")
            section(out, "HID REPORT DESCRIPTOR")
            desc = get_descriptor(fd)
            out.write(f"Length: {len(desc)} bytes\n\n")
            out.write(hexdump(desc) + "\n")
            parsed = parse_descriptor(desc)
            section(out, "PARSED REPORT SUMMARY")
            out.write("ID   INPUT_BYTES   OUTPUT_BYTES   FEATURE_BYTES   TOTAL_NOTES\n")
            out.write("-" * 72 + "\n")
            for rid, d in sorted(parsed.items()):
                notes = []
                if d["input"]:
                    notes.append("IN")
                if d["output"]:
                    notes.append("OUT")
                if d["feature"]:
                    notes.append("FEATURE")
                out.write(f"0x{rid:02X} {d['input']:12} {d['output']:14} {d['feature']:15} {'+'.join(notes)}\n")
            section(out, "FEATURE GET RESULTS")
            for rid, d in sorted(parsed.items()):
                if not d["feature"]:
                    continue
                total_size = d["feature"] + 1
                out.write(f"--- 0x{rid:02X}, {total_size} bytes ---\n")
                try:
                    data = feature_get(fd, rid, total_size)
                    out.write(data.hex(" ") + "\n")
                except OSError as exc:
                    out.write(f"GET_FEATURE ERROR: {exc}\n")
                out.write("\n")
            passive_capture(out, fd, max(0.0, args.seconds), 512)
            section(out, "END")
            out.write("This file contains raw observations for reverse engineering.\n")
    finally:
        os.close(fd)
    print(f"Saved: {output.resolve()}")


if __name__ == "__main__":
    raise SystemExit(main())
