CXX = g++
CC = gcc
CFLAGS = -O1 -g
CXXSRCS = matadd-driver.cpp
SSRCS = matadd.s
OBJECTS = $(addprefix obj/, $(notdir $(CXXSRCS:.cpp=.o) $(SSRCS:.s=.o)))
_xxxdir := $(shell mkdir -p obj)
BIN = matadd

all: $(BIN)
	@echo "...."
	@echo "Build complete"
	@echo "Run : ./$(BIN) > outfile"

$(BIN): $(sort $(OBJECTS))
	$(CXX) $^ $(CFLAGS) -o $@

$(addprefix obj/, $(SSRCS:.s=.o)): $(SSRCS)
	$(CC) $(CFLAGS) -c $< -o $@

$(addprefix obj/, $(CXXSRCS:.cpp=.o)): $(CXXSRCS)
	$(CXX) $(CFLAGS) -c $< -o $@

run:
	./$(BIN) > outfile
	diff -q outfile output.gold

clean:
	rm -f $(OBJECTS) $(BIN)
