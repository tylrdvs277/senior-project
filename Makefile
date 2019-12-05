PYTHON=python3
TARGET=milestone3.py
MAKE=make
ECHO=$?

all: assemble build test

assemble: $(TARGET)
	@echo "Building .s files"
	@echo
	@echo "addwithprint, dest addwithprint/addwithprint.s"
	$(PYTHON) $(TARGET) addwithprint/addwithprint.c.212r.expand addwithprint/addwithprint.s
	@echo
	@echo "regtest1, dest reg-test/regtest1.s"
	$(PYTHON) $(TARGET) reg-test/regtest1.c.212r.expand reg-test/regtest1.s
	@echo
	@echo "regtest2, dest reg-test/regtest2.s"
	$(PYTHON) $(TARGET) reg-test/regtest2.c.212r.expand reg-test/regtest2.s
	@echo
	@echo "matadd, dest matadd/matadd.s"
	$(PYTHON) $(TARGET) matadd/matadd.cpp.212r.expand matadd/matadd.s
	@echo

build: assemble
	@echo "Compiling executables"
	@echo
	@echo "Build addwithprint in addwithprint/"
	@$(MAKE) -C addwithprint -f Makefile 
	@echo
	@echo "Build regtest in reg-test/"
	@$(MAKE) -C reg-test -f Makefile 
	@echo
	@echo "Build matadd in matadd/"
	@$(MAKE) -C matadd -f Makefile.s
	@echo
	@echo

test: build
	@echo "Running executables and checking output"
	@echo
	@echo "Test addwithprint"
	@$(MAKE) -C addwithprint -f Makefile run
	@echo
	@echo "Test regtest"
	reg-test/regtest
	@echo
	@echo "Test matadd"
	@$(MAKE) -C matadd -f Makefile.s run	
	@echo

clean:
	@echo "Cleaning"
	@echo
	$(MAKE) -C addwithprint -f Makefile clean
	@echo
	$(MAKE) -C reg-test -f Makefile clean
	@echo
	$(MAKE) -C matadd -f Makefile.s clean
	@echo
