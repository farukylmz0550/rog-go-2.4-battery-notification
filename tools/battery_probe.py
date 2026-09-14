#!/usr/bin/env python3

import fcntl
import glob
import os
import sys
import time


VID = 0x0B05
PID = 0x18D6

REPORT_ID = 0xFF
REPORT_LENGTH = 64

BATTERY_QUERY = bytes([
    REPORT_ID,
    0x08,
    0x00,
    0xFD,
    0x04,
    0x12,
    0xF1,
    0x03,
    0x52,
    0x01,
])


# Linux hidraw ioctl definitions.
#
# _IOC(dir, type, nr, size)
def _ioc(direction, ioctl_type, number, size):
    return (
        (direction << 30)
        | (size << 16)
        | (ioctl_type << 8)
        | number
    )


IOC_WRITE = 1
IOC_READ = 2
HIDRAW_TYPE = ord("H")

HIDIOCSFEATURE = _ioc(
    IOC_READ | IOC_WRITE,
    HIDRAW_TYPE,
    0x06,
    REPORT_LENGTH,
)

HIDIOCGFEATURE = _ioc(
    IOC_READ | IOC_WRITE,
    HIDRAW_TYPE,
    0x07,
    REPORT_LENGTH,
)


def read_sysfs(path):
    try:
        with open(path, "r", encoding="ascii") as file:
            return file.read().strip()
    except OSError:
        return None


def find_device():
    """
    Find a hidraw device matching the ROG Strix Go 2.4 VID/PID.

    Prefer the MI_03 HID interface because that is the interface
    used for the headset battery feature report.
    """

    candidates = []

    for hidraw in glob.glob("/dev/hidraw*"):
        name = os.path.basename(hidraw)
        sysfs = f"/sys/class/hidraw/{name}/device"

        try:
            real_path = os.path.realpath(sysfs)
        except OSError:
            continue

        current = real_path

        while current != "/":
            vendor = read_sysfs(
                os.path.join(current, "idVendor")
            )
            product = read_sysfs(
                os.path.join(current, "idProduct")
            )

            if vendor and product:
                try:
                    vendor_id = int(vendor, 16)
                    product_id = int(product, 16)
                except ValueError:
                    break

                if vendor_id == VID and product_id == PID:
                    priority = (
                        0 if "MI_03" in real_path else 1
                    )

                    candidates.append(
                        (priority, hidraw, real_path)
                    )

                break

            current = os.path.dirname(current)

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0])

    return candidates[0]


def hex_dump(data):
    return " ".join(
        f"{byte:02X}" for byte in data
    )


def main():
    device = find_device()

    if device is None:
        print(
            f"ROG Strix Go 2.4 not found "
            f"(VID:PID {VID:04X}:{PID:04X})."
        )
        sys.exit(1)

    _, hidraw_path, sysfs_path = device

    print(f"Device: {hidraw_path}")
    print(f"Sysfs:  {sysfs_path}")
    print(f"VID:PID {VID:04X}:{PID:04X}")
    print()

    # G-Helper sends this feature report and pads it
    # to 64 bytes.
    query = BATTERY_QUERY.ljust(
        REPORT_LENGTH,
        b"\x00",
    )

    print("SET_FEATURE:")
    print(hex_dump(query))
    print()

    try:
        fd = os.open(
            hidraw_path,
            os.O_RDWR,
        )
    except PermissionError:
        print(
            f"Permission denied: {hidraw_path}"
        )
        print(
            "Check the device permissions or "
            "udev rules."
        )
        sys.exit(1)
    except OSError as exc:
        print(
            f"Could not open {hidraw_path}: "
            f"{exc}"
        )
        sys.exit(1)

    try:
        # Send the battery query.
        set_buffer = bytearray(query)

        try:
            result = fcntl.ioctl(
                fd,
                HIDIOCSFEATURE,
                set_buffer,
                True,
            )
        except OSError as exc:
            print(
                "HIDIOCSFEATURE failed: "
                f"[{exc.errno}] {exc.strerror}"
            )
            sys.exit(1)

        print(
            f"HIDIOCSFEATURE result: {result}"
        )

        # G-Helper waits approximately 35 ms between
        # SET_FEATURE and GET_FEATURE.
        time.sleep(0.035)

        print()
        print("GET_FEATURE attempts:")

        found_battery = False

        for attempt in range(1, 6):
            get_buffer = bytearray(
                REPORT_LENGTH
            )

            # Request feature report 0xFF.
            get_buffer[0] = REPORT_ID

            try:
                result = fcntl.ioctl(
                    fd,
                    HIDIOCGFEATURE,
                    get_buffer,
                    True,
                )
            except OSError as exc:
                print(
                    f"Attempt {attempt}: "
                    "HIDIOCGFEATURE failed: "
                    f"[{exc.errno}] "
                    f"{exc.strerror}"
                )
                time.sleep(0.035)
                continue

            response = bytes(get_buffer)

            print(
                f"Attempt {attempt}: "
                f"{hex_dump(response)}"
            )

            # Expected G-Helper response starts with:
            #
            # FF 1B 05 FE ...
            #
            # Byte 13 contains battery percentage.
            if (
                len(response) >= 14
                and response[0] == REPORT_ID
                and response[1] == 0x1B
            ):
                battery = response[13]

                if battery <= 100:
                    print()
                    print(
                        f"Battery: {battery}%"
                    )

                    found_battery = True
                    break

            time.sleep(0.035)

        if not found_battery:
            print()
            print(
                "No valid battery response received."
            )
            print(
                "The device responded, but the "
                "expected G-Helper battery report "
                "was not returned."
            )

            sys.exit(1)

    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
