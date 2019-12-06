PYTHON=python3
TARGET=src/milestone4.py
MAKE=make
ECHO=$?

all: assemble build test

assemble: $(TARGET)
	@echo "Building .s files"
	@echo
	@echo "matadd, dest matadd/matadd.s"
	$(PYTHON) $(TARGET) matadd/matadd.cpp.212r.expand matadd/matadd.s
	@echo

build: assemble
	@echo "Compiling executables"
	@echo
	@echo "Build matadd in matadd/"
	@$(MAKE) -C matadd -f Makefile.s
	@echo

test: build
	@echo "Running executables and checking output"
	@echo
	@echo "Test matadd"
	@$(MAKE) -C matadd -f Makefile.s run	
	@echo

clean:
	@echo "Cleaning"
	@echo
	$(MAKE) -C matadd -f Makefile.s clean
	@echo
