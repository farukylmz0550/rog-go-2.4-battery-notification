#include <errno.h>
#include <fcntl.h>
#include <linux/hidraw.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

#include "battery.h"
#include "util.h"

/* Feature report ID used by the battery query. */
#define ROG_REPORT_ID 0xFF

/*
 * Known battery query from G-Helper PR #5159:
 *
 *   FF 08 00 FD 04 12 F1 03 52 01
 *
 * The remainder of the 64-byte buffer must be zero.
 */
static const unsigned char battery_query[] = {
    0xFF, 0x08, 0x00, 0xFD, 0x04,
    0x12, 0xF1, 0x03, 0x52, 0x01
};

/*
 * Expected 2.4 GHz battery response type:
 *
 *   FF 1B 05 FE 12 04 1F 14 01 03 05 XX 0D YY ...
 *
 * response[13] carries the reported battery value.
 * In 3.5 mm analog mode the device answers with type 0x01 instead;
 * that response is not treated as a battery answer and is rejected.
 */
#define ROG_RESPONSE_TYPE          0x1B
#define ROG_RESPONSE_BATTERY_INDEX 13

static void print_hex(FILE *stream, const unsigned char *data, size_t length)
{
    for (size_t i = 0; i < length; i++)
        fprintf(stream, i + 1 < length ? "%02X " : "%02X\n", data[i]);
}

static void print_debug(
    const char *label,
    const unsigned char *data,
    size_t length
)
{
    char stamp[9];
    time_t now = time(NULL);

    strftime(stamp, sizeof(stamp), "%H:%M:%S", localtime(&now));
    fprintf(stderr, "[%s] %s (%zu bytes):\n", stamp, label, length);
    print_hex(stderr, data, length);
}

static bool is_disconnect_error(int error)
{
    return error == ENODEV || error == ENOENT || error == ENXIO;
}

enum rog_battery_status rog_battery_read(
    const char *devnode,
    unsigned char *percent,
    bool debug
)
{
    unsigned char request[ROG_FEATURE_REPORT_LENGTH] = {0};
    unsigned char response[ROG_FEATURE_REPORT_LENGTH] = {0};
    int fd;
    int result;

    fd = open(devnode, O_RDWR);
    if (fd < 0) {
        if (errno == EACCES) {
            fprintf(
                stderr,
                "Permission denied for %s.\n"
                "Add a udev rule or a uaccess tag for this user, "
                "e.g. a udev rule with MODE=\"0660\" and GROUP matching "
                "your user, then replug the dongle.\n",
                devnode
            );
            return ROG_BATTERY_PERMISSION;
        }

        if (is_disconnect_error(errno))
            return ROG_BATTERY_DISCONNECT;

        fprintf(stderr, "Failed to open %s: %s\n", devnode, strerror(errno));
        return ROG_BATTERY_IO;
    }

    memcpy(request, battery_query, sizeof(battery_query));

    result = ioctl(fd, HIDIOCSFEATURE(ROG_FEATURE_REPORT_LENGTH), request);
    if (result < 0) {
        if (is_disconnect_error(errno)) {
            close(fd);
            return ROG_BATTERY_DISCONNECT;
        }
        fprintf(
            stderr,
            "HIDIOCSFEATURE failed on %s: %s\n",
            devnode,
            strerror(errno)
        );
        close(fd);
        return ROG_BATTERY_IO;
    }

    /*
     * G-Helper waits ~35 ms between SET_FEATURE and GET_FEATURE;
     * the firmware needs this gap to prepare the answer.
     */
    sleep_ms(35);

    /* The report ID selects which report GET_FEATURE reads. */
    response[0] = ROG_REPORT_ID;

    result = ioctl(fd, HIDIOCGFEATURE(ROG_FEATURE_REPORT_LENGTH), response);
    close(fd);

    if (result < 0) {
        if (is_disconnect_error(errno))
            return ROG_BATTERY_DISCONNECT;
        fprintf(
            stderr,
            "HIDIOCGFEATURE failed on %s: %s\n",
            devnode,
            strerror(errno)
        );
        return ROG_BATTERY_IO;
    }

    if (debug) {
        print_debug("SET_FEATURE", request, sizeof(request));
        print_debug("GET_FEATURE", response, (size_t)result);
    }

    if (result < ROG_RESPONSE_BATTERY_INDEX + 1) {
        fprintf(
            stderr,
            "Short GET_FEATURE response: %d bytes (expected %d)\n",
            result,
            ROG_RESPONSE_BATTERY_INDEX + 1
        );
        return ROG_BATTERY_IO;
    }

    if (response[0] != ROG_REPORT_ID) {
        fprintf(stderr, "Unexpected report ID: 0x%02X\n", response[0]);
        return ROG_BATTERY_RESPONSE;
    }

    if (response[1] != ROG_RESPONSE_TYPE) {
        fprintf(
            stderr,
            "Unexpected response type: 0x%02X "
            "(battery value not read from unknown responses)\n",
            response[1]
        );
        return ROG_BATTERY_RESPONSE;
    }

    if (response[ROG_RESPONSE_BATTERY_INDEX] > 100) {
        fprintf(
            stderr,
            "Invalid battery value: %u\n",
            response[ROG_RESPONSE_BATTERY_INDEX]
        );
        return ROG_BATTERY_RESPONSE;
    }

    *percent = response[ROG_RESPONSE_BATTERY_INDEX];

    return ROG_BATTERY_OK;
}
