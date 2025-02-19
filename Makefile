PYTHON=python3
TARGET=src/driver.py
MAKE=make
ECHO=$?

all: assemble build test

assemble: $(TARGET)
	@echo "Building .s files"
	@echo
	@echo "matadd, dest matadd/matadd.s"
	$(PYTHON) $(TARGET) matadd/matadd.cpp.212r.expand matadd/matadd.s
	@echo
	@echo "regtest1, dest reg-test/regtest1.s"
	$(PYTHON) $(TARGET) reg-test/regtest1.c.212r.expand reg-test/regtest1.s
	@echo
	@echo "regtest2, dest reg-test/regtest2.s"
	$(PYTHON) $(TARGET) reg-test/regtest2.c.212r.expand reg-test/regtest2.s
	@echo
	@echo "trace, dest trace/trace.s"
	$(PYTHON) $(TARGET) trace/trace.c.234r.expand trace/trace.s
	@echo

assemble_no_schedule: $(TARGET)
	@echo "Building .s files with no scheduling"
	@echo
	@echo "matadd, dest matadd/matadd.s"
	NO_SCHEDULE=1 $(PYTHON) $(TARGET) matadd/matadd.cpp.212r.expand matadd/matadd.s
	@echo
	@echo "regtest1, dest reg-test/regtest1.s"
	NO_SCHEDULE=1 $(PYTHON) $(TARGET) reg-test/regtest1.c.212r.expand reg-test/regtest1.s
	@echo
	@echo "regtest2, dest reg-test/regtest2.s"
	NO_SCHEDULE=1 $(PYTHON) $(TARGET) reg-test/regtest2.c.212r.expand reg-test/regtest2.s
	@echo
	@echo "trace, dest trace/trace.s"
	NO_SCHEDULE=1 $(PYTHON) $(TARGET) trace/trace.c.234r.expand trace/trace.s
	@echo

build: assemble
	@echo "Compiling executables"
	@echo
	@echo "Build matadd in matadd/"
	@$(MAKE) -C matadd -f Makefile.s
	@echo
	@echo "Build regtest in reg-test/"
	@$(MAKE) -C reg-test -f Makefile
	@echo
	@echo "Build trace in trace/"
	@$(MAKE) -C trace -f Makefile.s
	@echo

build_no_schedule: assemble_no_schedule
	@echo "Compiling executables"
	@echo
	@echo "Build matadd in matadd/"
	@$(MAKE) -C matadd -f Makefile.s
	@echo
	@echo "Build regtest in reg-test/"
	@$(MAKE) -C reg-test -f Makefile
	@echo
	@echo "Build trace in trace/"
	@$(MAKE) -C trace -f Makefile.s
	@echo

test: build
	@echo "Running executables and checking output"
	@echo
	@echo "Test matadd"
	@$(MAKE) -C matadd -f Makefile.s run
	@echo
	@echo "Test regtest"
	reg-test/regtest
	@echo
	@echo "Test trace"
	@$(MAKE) -C trace -f Makefile.s run
	@echo

clean:
	@echo "Cleaning"
	@echo
	$(MAKE) -C matadd -f Makefile.s clean
	@echo
	$(MAKE) -C reg-test -f Makefile clean
	@echo
	$(MAKE) -C vecsort -f Makefile.s clean
	@echo
