#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "battery.h"
#include "device.h"
#include "util.h"

/* Battery polling interval while the headset is connected. */
#define POLL_INTERVAL_MS 30000

/* Device rescan interval while the headset is disconnected. */
#define SCAN_INTERVAL_MS 3000

/*
 * Disconnect watch granularity. The hidraw node is checked every
 * second between battery polls, so a dongle removal is noticed
 * within ~1 s instead of up to a full poll interval later.
 */
#define WATCH_SLICE_MS 1000

static void usage(FILE *stream)
{
    fprintf(
        stream,
        "Usage: rog-go-battery [--once] [--debug] [--help]\n"
        "\n"
        "  --once   Read the battery once and exit.\n"
        "           Exit status: 0 success, 1 failure/device absent.\n"
        "  --debug  Also dump raw SET_FEATURE/GET_FEATURE bytes to stderr.\n"
        "  --help   Show this help.\n"
        "\n"
        "Without --once the program keeps running: it prints the battery\n"
        "level when it changes and automatically rediscovers the headset\n"
        "after a disconnect/reconnect of the USB dongle.\n"
    );
}

static void print_not_found(void)
{
    fprintf(
        stderr,
        "ROG Strix Go 2.4 not found "
        "(VID:PID %04X:%04X, interface MI_03).\n",
        ROG_VENDOR_ID,
        ROG_PRODUCT_ID
    );
}

static int run_once(bool debug)
{
    char path[ROG_DEVICE_PATH_MAX];
    unsigned char percent;
    enum rog_battery_status status;

    printf("Searching for ROG Strix Go 2.4...\n");

    if (rog_device_find(path, sizeof(path)) != ROG_DEVICE_FOUND) {
        print_not_found();
        return EXIT_FAILURE;
    }

    printf("Device connected: %s\n", path);

    status = rog_battery_read(path, &percent, debug);
    if (status != ROG_BATTERY_OK) {
        fprintf(stderr, "Battery read failed.\n");
        return EXIT_FAILURE;
    }

    printf("Battery: %u%%\n", percent);

    return EXIT_SUCCESS;
}

static void print_disconnected(void)
{
    printf("Device disconnected.\n");
    printf("Waiting for device...\n");
}

static int run_monitor(bool debug)
{
    char path[ROG_DEVICE_PATH_MAX];
    bool connected = false;
    int last = -1;

    printf("Searching for ROG Strix Go 2.4...\n");

    for (;;) {
        unsigned char percent;
        enum rog_battery_status status;

        if (!connected) {
            enum rog_device_result found =
                rog_device_find(path, sizeof(path));

            if (found == ROG_DEVICE_ERROR)
                return EXIT_FAILURE;

            if (found != ROG_DEVICE_FOUND) {
                sleep_ms(SCAN_INTERVAL_MS);
                continue;
            }

            printf("Device connected: %s\n", path);
            connected = true;
            last = -1;
        }

        status = rog_battery_read(path, &percent, debug);

        switch (status) {
        case ROG_BATTERY_OK:
            if ((int)percent != last) {
                printf("Battery: %u%%\n", percent);
                last = percent;
            }

            /*
             * Wait for the next poll, but watch the devnode in
             * 1 s slices so a dongle removal is noticed promptly.
             */
            for (int waited = 0; waited < POLL_INTERVAL_MS; waited += WATCH_SLICE_MS) {
                sleep_ms(WATCH_SLICE_MS);
                if (access(path, F_OK) != 0) {
                    connected = false;
                    last = -1;
                    print_disconnected();
                    break;
                }
            }
            break;

        case ROG_BATTERY_DISCONNECT:
            connected = false;
            last = -1;
            print_disconnected();
            sleep_ms(SCAN_INTERVAL_MS);
            break;

        case ROG_BATTERY_PERMISSION:
            /* Won't heal on its own: stop instead of looping forever. */
            return EXIT_FAILURE;

        default:
            /*
             * Transient I/O or unrecognized response (e.g. the 0x01
             * type observed right after reconnect): retry soon.
             */
            sleep_ms(SCAN_INTERVAL_MS);
            break;
        }
    }
}

int main(int argc, char **argv)
{
    bool once = false;
    bool debug = false;

    /*
     * Line-buffered stdout even when redirected to a file or pipe,
     * so status lines survive termination (SIGTERM/SIGINT) without
     * a pending full 4 KiB buffer.
     */
    setvbuf(stdout, NULL, _IOLBF, 0);

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--once") == 0) {
            once = true;
        } else if (strcmp(argv[i], "--debug") == 0) {
            debug = true;
        } else if (strcmp(argv[i], "--help") == 0 ||
                   strcmp(argv[i], "-h") == 0) {
            usage(stdout);
            return EXIT_SUCCESS;
        } else {
            fprintf(stderr, "Unknown option: %s\n", argv[i]);
            usage(stderr);
            return EXIT_FAILURE;
        }
    }

    return once ? run_once(debug) : run_monitor(debug);
}
