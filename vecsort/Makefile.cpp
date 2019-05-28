CXX = g++
CFLAGS = -O1 -Wall -g
SRCS = vecsort.cpp driver.cpp 
BIN = vecsort

all:
	$(CXX) -D_CPP_ $(CFLAGS) -o $(BIN) $(SRCS)

clean:
	rm -f $(BIN) *.o
