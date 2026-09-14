#include <errno.h>
#include <time.h>

#include "util.h"

void sleep_ms(long milliseconds)
{
    struct timespec request;

    request.tv_sec = milliseconds / 1000;
    request.tv_nsec = (milliseconds % 1000) * 1000000L;

    while (nanosleep(&request, &request) == -1 && errno == EINTR)
        continue;
}
