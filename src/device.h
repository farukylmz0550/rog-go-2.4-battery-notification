#ifndef ROG_DEVICE_H
#define ROG_DEVICE_H

#include <stddef.h>

/* USB identification of the ROG Strix Go 2.4 dongle. */
#define ROG_VENDOR_ID        0x0B05
#define ROG_PRODUCT_ID       0x18D6

/*
 * The battery Feature Report interface is MI_03 on the composite
 * dongle. The hidraw character device belonging to this interface
 * must be discovered dynamically; hidraw numbering is not stable
 * across re-enumeration.
 */
#define ROG_INTERFACE_NUMBER 3

#define ROG_DEVICE_PATH_MAX  256

enum rog_device_result {
    ROG_DEVICE_FOUND     = 0,
    ROG_DEVICE_NOT_FOUND = 1,
    ROG_DEVICE_ERROR     = -1
};

/*
 * Search every hidraw device exposed by udev and return the devnode
 * of the one owned by the ROG Strix Go 2.4 MI_03 USB interface.
 *
 * Returns ROG_DEVICE_FOUND and fills `path` on success,
 * ROG_DEVICE_NOT_FOUND when no matching device is present, or
 * ROG_DEVICE_ERROR when the udev context itself cannot be used.
 */
enum rog_device_result rog_device_find(char *path, size_t size);

#endif
