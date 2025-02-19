CXX = g++
CC = gcc
CFLAGS = -O1
CXXSRCS = driver.cpp
SSRCS = vecsort.s
OBJECTS = $(addprefix obj/, $(notdir $(CXXSRCS:.cpp=.o) $(SSRCS:.s=.o)))
_xxxdir := $(shell mkdir -p obj)
BIN = vecsort

all: $(BIN)
	@echo "...."
	@echo "Build complete"
	@echo "Run : ./vecsort > outfile"

$(BIN): $(sort $(OBJECTS))
	$(CXX) $^ $(CFLAGS) -o $@

$(addprefix obj/, $(SSRCS:.s=.o)): $(SSRCS)
	$(CC) $(CFLAGS) -c $< -o $@

$(addprefix obj/, $(CXXSRCS:.cpp=.o)): $(CXXSRCS)
	$(CXX) $(CFLAGS) -c $< -o $@

run:
	./$(BIN) > outfile
	diff -q outfile vector.sorted

clean:
	rm -f $(OBJECTS) $(BIN) outfile
