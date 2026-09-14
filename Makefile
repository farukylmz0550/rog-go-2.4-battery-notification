CC      ?= cc
CFLAGS  ?= -std=c11 -Wall -Wextra -O2
CFLAGS  += -D_POSIX_C_SOURCE=200809L
LDLIBS   = -ludev

SRC = src/main.c src/device.c src/battery.c src/util.c
OBJ = $(SRC:.c=.o)
BIN = rog-go-battery

.PHONY: all clean

all: $(BIN)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDLIBS)

src/%.o: src/%.c src/*.h
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(BIN) $(OBJ)
