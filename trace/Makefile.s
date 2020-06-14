CC = gcc
CFLAGS = -O1 -g
CCSRCS = driver.c
SSRCS = trace.s
BIN = trace

all: $(BIN)
	@echo "...."
	@echo "Build complete"
	@echo "Run : ./$(BIN) > outfile"

$(BIN): $(CCSRCS) $(SSRCS)
	$(CC) $^ $(CFLAGS) -o $@

run:
	./$(BIN) > outfile
	diff -q outfile output.gold

clean:
	rm -f $(OBJECTS) $(BIN)
