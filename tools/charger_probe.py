#!/usr/bin/env python3

"""
Probe the 0B05:18D7 "ROG STRIX Go 2.4 Headset Battery Charger" HID
device (the headset itself, enumerated while its USB-C cable is
connected to the PC).

Its HID report descriptor differs from the 18D6 dongle:

  - report 0xFF: a 32-bit INPUT field plus a 1-byte FEATURE field
  - report 0xFD: an 8-bit INPUT field and button inputs

This tool deliberately performs read-only operations only
(HIDIOCGFEATURE requests and a passive read loop). No commands are
sent to the device, and no byte is interpreted as charging state.
"""

import fcntl
import glob
import os
import sys
import time
from datetime import datetime

VID = 0x0B05
PID = 0x18D7

FEATURE_ATTEMPTS = [
    # (report_id, buffer_length)
    (0xFF, 64),
    (0xFF, 2),
    (0xFD, 64),
    (0xFD, 2),
]

PASSIVE_READ_SECONDS = 20


def _ioc(direction, ioctl_type, number, size):
    return (
        (direction << 30)
        | (size << 16)
        | (ioctl_type << 8)
        | number
    )


# HIDIOCGFEATURE is defined as _IOC(_IOC_READ|_IOC_WRITE, 'H', 0x07,
# len): the buffer is written by the caller (report id) and read back
# by the kernel. Direction READ only causes EINVAL on some kernels.
IOC_RDWR = 1 | 2
HIDRAW_TYPE = ord("H")


def hidraw_get_feature(size):
    return _ioc(
        IOC_RDWR,
        HIDRAW_TYPE,
        0x07,
        size,
    )


def read_sysfs(path):
    try:
        with open(path, "r", encoding="ascii") as file:
            return file.read().strip()
    except OSError:
        return None


def find_device():
    """
    Find the hidraw node belonging to the 0B05:18D7 USB device.
    """
    for hidraw in glob.glob("/dev/hidraw*"):
        name = os.path.basename(hidraw)
        current = os.path.realpath(
            f"/sys/class/hidraw/{name}/device"
        )

        while current != "/":
            vendor = read_sysfs(os.path.join(current, "idVendor"))
            product = read_sysfs(os.path.join(current, "idProduct"))

            if vendor and product:
                if (
                    int(vendor, 16) == VID
                    and int(product, 16) == PID
                ):
                    return hidraw, current
                break

            current = os.path.dirname(current)

    return None


def hex_dump(data):
    return " ".join(f"{byte:02X}" for byte in data)


def timestamp():
    return datetime.now().strftime("%H:%M:%S")


def get_feature(fd, report_id, size):
    buffer = bytearray(size)
    buffer[0] = report_id

    try:
        result = fcntl.ioctl(
            fd,
            hidraw_get_feature(size),
            buffer,
            True,
        )
    except OSError as exc:
        return f"HIDIOCGFEATURE failed: [{exc.errno}] {exc.strerror}"

    return f"{result} bytes: {hex_dump(bytes(buffer[:result]))}"


def passive_read(fd, seconds):
    """
    Print any spontaneous input reports for a limited window.
    """
    os.set_blocking(fd, False)
    deadline = time.monotonic() + PASSIVE_READ_SECONDS

    print(f"--- passive read for {PASSIVE_READ_SECONDS} s ---")

    while time.monotonic() < deadline:
        try:
            data = os.read(fd, 64)
            print(f"[{timestamp()}] INPUT: {hex_dump(data)}")
        except BlockingIOError:
            time.sleep(0.25)
        except OSError as exc:
            print(f"read failed: [{exc.errno}] {exc.strerror}")
            break

    os.set_blocking(fd, True)


def main():
    device = find_device()

    if device is None:
        print(f"0B05:{PID:04X} HID device not found.")
        sys.exit(1)

    hidraw_path, usb_sysfs = device

    print(f"Device: {hidraw_path}")
    print(f"Sysfs:  {usb_sysfs}")
    print(f"VID:PID {VID:04X}:{PID:04X}")
    print()

    # The report descriptor lives on the HID device (child of the
    # USB interface), one level below the USB device that was
    # matched by VID/PID.
    descriptor_path = os.path.join(
        os.path.realpath(
            f"/sys/class/hidraw/{os.path.basename(hidraw_path)}/device"
        ),
        "report_descriptor",
    )

    try:
        with open(descriptor_path, "rb") as file:
            descriptor = file.read()
        print(f"Report descriptor ({len(descriptor)} bytes):")
        print(hex_dump(descriptor))
    except OSError as exc:
        print(f"Could not read descriptor: {exc}")

    print()

    try:
        fd = os.open(hidraw_path, os.O_RDWR)
    except PermissionError:
        print(f"Permission denied: {hidraw_path}")
        print("Install the uaccess udev rule for 18D7 or use sudo.")
        sys.exit(1)
    except OSError as exc:
        print(f"Could not open {hidraw_path}: {exc}")
        sys.exit(1)

    try:
        print("--- GET_FEATURE attempts ---")
        for report_id, size in FEATURE_ATTEMPTS:
            result = get_feature(fd, report_id, size)
            print(f"[{timestamp()}] report 0x{report_id:02X} "
                  f"(buffer {size}): {result}")

        passive_read(fd, PASSIVE_READ_SECONDS)
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
