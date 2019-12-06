CXX = g++
CFLAGS = -O1 -Wall -g
SRCS = matadd.cpp matadd-driver.cpp 
BIN = matadd

all:
	$(CXX) -D_CPP_ $(CFLAGS) -o $(BIN) $(SRCS)

clean:
	rm -f $(BIN)
