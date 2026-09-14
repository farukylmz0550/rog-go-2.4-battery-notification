#ifndef ROG_BATTERY_H
#define ROG_BATTERY_H

#include <stdbool.h>

/*
 * The battery exchange uses a 64-byte Feature Report on report ID
 * 0xFF, as documented by G-Helper PR #5159.
 */
#define ROG_FEATURE_REPORT_LENGTH 64

enum rog_battery_status {
    ROG_BATTERY_OK         = 0,
    ROG_BATTERY_DISCONNECT = -1, /* device gone (or vanished mid-read) */
    ROG_BATTERY_PERMISSION = -2, /* hidraw open denied (udev rule needed) */
    ROG_BATTERY_RESPONSE   = -3, /* answer received but not recognized */
    ROG_BATTERY_IO         = -4  /* open/ioctl failure, device still there */
};

/*
 * Perform one battery query against `devnode`:
 *
 *   open -> HIDIOCSFEATURE (64-byte query) -> ~35 ms wait ->
 *   HIDIOCGFEATURE -> validate -> extract percentage
 *
 * The device node is opened and closed per query. This is
 * intentional: a long-lived fd cannot survive a dongle
 * re-enumeration, and reopening per poll cycle removes an entire
 * class of stale-fd bugs.
 *
 * When `debug` is true, the raw exchange is written to stderr with
 * a timestamp, for protocol research captures.
 *
 * Only the battery percentage is extracted. Unknown bytes are never
 * interpreted (charging state detection is deliberately not
 * implemented; the byte is not yet confirmed by protocol research).
 */
enum rog_battery_status rog_battery_read(
    const char *devnode,
    unsigned char *percent,
    bool debug
);

#endif
