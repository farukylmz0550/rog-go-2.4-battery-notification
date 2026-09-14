#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <libudev.h>

#include "device.h"

/*
 * Discovery works through the udev database rather than a fixed
 * /dev/hidrawN path:
 *
 *   hidraw device
 *     -> parent USB interface (bInterfaceNumber == 3, i.e. MI_03)
 *       -> parent USB device (idVendor == 0B05, idProduct == 18D6)
 *
 * The dongle enumerates as a composite device; only the MI_03
 * interface speaks the battery Feature Report protocol.
 */
enum rog_device_result rog_device_find(char *path, size_t size)
{
    struct udev *udev;
    struct udev_enumerate *enumerate;
    struct udev_list_entry *devices;
    struct udev_list_entry *entry;

    udev = udev_new();
    if (!udev) {
        fprintf(stderr, "Failed to create udev context.\n");
        return ROG_DEVICE_ERROR;
    }

    enumerate = udev_enumerate_new(udev);
    if (!enumerate) {
        fprintf(stderr, "Failed to create udev enumerator.\n");
        udev_unref(udev);
        return ROG_DEVICE_ERROR;
    }

    if (udev_enumerate_add_match_subsystem(enumerate, "hidraw") < 0 ||
        udev_enumerate_scan_devices(enumerate) < 0) {
        fprintf(stderr, "Failed to scan hidraw devices.\n");
        udev_enumerate_unref(enumerate);
        udev_unref(udev);
        return ROG_DEVICE_ERROR;
    }

    devices = udev_enumerate_get_list_entry(enumerate);

    udev_list_entry_foreach(entry, devices) {
        const char *syspath = udev_list_entry_get_name(entry);
        struct udev_device *hidraw;
        struct udev_device *usb_interface;
        struct udev_device *usb_device;
        const char *interface_number;
        const char *vendor;
        const char *product;
        const char *devnode;

        hidraw = udev_device_new_from_syspath(udev, syspath);
        if (!hidraw)
            continue;

        usb_interface = udev_device_get_parent_with_subsystem_devtype(
            hidraw, "usb", "usb_interface");
        if (!usb_interface) {
            udev_device_unref(hidraw);
            continue;
        }

        interface_number = udev_device_get_sysattr_value(
            usb_interface, "bInterfaceNumber");
        if (!interface_number ||
            (int)strtol(interface_number, NULL, 16) != ROG_INTERFACE_NUMBER) {
            udev_device_unref(hidraw);
            continue;
        }

        /*
         * idVendor/idProduct live on the USB *device*, one level
         * above the interface.
         */
        usb_device = udev_device_get_parent_with_subsystem_devtype(
            usb_interface, "usb", "usb_device");
        if (!usb_device) {
            udev_device_unref(hidraw);
            continue;
        }

        vendor = udev_device_get_sysattr_value(usb_device, "idVendor");
        product = udev_device_get_sysattr_value(usb_device, "idProduct");
        if (!vendor || !product ||
            (int)strtol(vendor, NULL, 16) != ROG_VENDOR_ID ||
            (int)strtol(product, NULL, 16) != ROG_PRODUCT_ID) {
            udev_device_unref(hidraw);
            continue;
        }

        devnode = udev_device_get_devnode(hidraw);
        if (devnode) {
            snprintf(path, size, "%s", devnode);
            udev_device_unref(hidraw);
            udev_enumerate_unref(enumerate);
            udev_unref(udev);
            return ROG_DEVICE_FOUND;
        }

        udev_device_unref(hidraw);
    }

    udev_enumerate_unref(enumerate);
    udev_unref(udev);

    return ROG_DEVICE_NOT_FOUND;
}
