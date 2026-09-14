#!/usr/bin/env python3

"""
Diff the battery query responses inside a charging-ramp capture file.

Parses the `GET_FEATURE (64 bytes):` / response-line pairs produced by
`rog-go-battery --debug` and prints, per byte index, how many distinct
values were observed and their change history. Constant bytes are
collapsed into one line; varying bytes are listed individually so a
battery-percentage candidate (monotonic rise during charging) stands
out.
"""

import re
import sys

RESPONSE_ID_LINE = re.compile(r"GET_FEATURE \((\d+) bytes\)")
HEX_LINE = re.compile(r"^([0-9A-F]{2}(?: [0-9A-F]{2})+)$")


def parse(path):
    responses = []
    timestamps = []

    with open(path, "r", encoding="ascii") as file:
        lines = file.read().splitlines()

    pending_time = None

    for line in lines:
        stamp = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]", line)
        if stamp:
            pending_time = stamp.group(1)
            continue

        if RESPONSE_ID_LINE.search(line):
            # The response follows on the next non-empty line.
            pending_response = True
            continue

        match = HEX_LINE.match(line)
        if match and responses and not timestamps[-1]:
            # Should not happen: each hex line belongs to either
            # SET_FEATURE or GET_FEATURE. Track by alternation below.
            pass

        if match:
            responses.append([int(x, 16) for x in line.split()])
            timestamps.append(pending_time)

    # Every debug exchange prints SET_FEATURE then GET_FEATURE; keep
    # only the even-indexed (GET_FEATURE) entries.
    responses = responses[1::2]
    timestamps = timestamps[1::2]

    return responses, timestamps


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "-"
    responses, timestamps = parse(path)

    if not responses:
        print("No responses found.")
        return

    length = max(len(r) for r in responses)
    print(f"{len(responses)} responses, first {timestamps[0]}, "
          f"last {timestamps[-1]}")
    print()

    varying = False
    for index in range(length):
        values = [r[index] for r in responses if len(r) > index]
        distinct = sorted(set(values))

        if len(distinct) == 1:
            print(f"byte {index:2d}: constant 0x{distinct[0]:02X}")
        else:
            varying = True
            print(f"byte {index:2d}: {len(distinct):2d} distinct "
                  f"values 0x{distinct[0]:02X}..0x{distinct[-1]:02X}")
            print(f"          series: "
                  + " ".join(f"{v:02X}" for v in values))

    if not varying:
        print()
        print("All bytes constant across the session.")


if __name__ == "__main__":
    import sys
    main()
