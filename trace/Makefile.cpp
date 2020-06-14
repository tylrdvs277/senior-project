CC = gcc
CFLAGS = -O1 -Wall -g
SRCS = trace.c driver.c 
BIN = trace

all:
	$(CC) $(CFLAGS) -o $(BIN) $(SRCS)

clean:
	rm -f $(BIN)
