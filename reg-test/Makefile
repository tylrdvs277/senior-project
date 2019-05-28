CC = gcc
CFLAGS = -g -Wall -O1
SRCS = driver.c regtest1.s regtest2.s
BIN = regtest

all:
	$(CC) $(CFLAGS) -c $(SRCS)
	$(CC) $(CFLAGS) -o $(BIN) *.o

clean:
	rm -f $(BIN) *.o
