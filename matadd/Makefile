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
	@echo "Run : ./matadd > outfile"

$(BIN): $(sort $(OBJECTS))
	$(CXX) $^ $(CFLAGS) -o $@

$(addprefix obj/, $(SSRCS:.s=.o)): $(SSRCS)
	$(CC) $(CFLAGS) -c $< -o $@

$(addprefix obj/, $(CXXSRCS:.cpp=.o)): $(CXXSRCS)
	$(CXX) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(BIN)
