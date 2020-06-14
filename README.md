# Trace Scheduling
## Tyler Davis (tylrdvs277)
### Build Instructions
* This requires some Python distribution to run (please use Python3 >=3.7)
* This implementation uses a Makefile to configure the environment and run on the provided input
* The Makefile has 7 targets: `all`, `assemble`, `assemble_no_schedule`, `build`, `build_no_schedule`, `test`, and `clean`
    * `all` (default/optional): runs `assemble`, `build`, and `test`
    * `assemble`: builds the .s files for matadd, regtest1, regtest2, and trace
    * `assemble_no_schedule`: builds the .s files without instruction scheduling
    * `build`: builds the complete program executables by invoking `make(1)` in the subdirectories
    * `build_no_schedule`: builds the programs using no instruction scheduling
    * `test`: run the executable and prints or runs `diff(1)` on the outputs except regtest
    * `clean`: removes object files by invoking `make clean` in the subdirectories
```
make [all|build|test|clean]
```
### Run Instructions
* If you want to run the program on another input file, the program can be invoked on its own
* Invoke the following command
```
python3 src/driver.py <input expand file> <output assembly file>
```
* The result will be that `<output assembly file>` contains the assembly language representation of the rtl
* If you do not want to use instruction scheduling, define the `NO_SCHEDULE` environment variable on the command line
```
export NO_SCHEDULE=1
```
### Code Structure
All the source code is contained in the `src/` directory which is layed out as followed:
  * `src/sexp`: Contains a sligthly modify sexp library from the internet. Used to read the rtl file.
  * `src/rtl`: This module contains the classes that define the internal representations of the rtl. This module has submodules that define the architecture registers and the values (the things the rtl operate on).
  * `src/graph`: This module defines the structures that define the control flow of the code and identify loops (used to find a spill candidate).
  * `src/liveness`: Contains the code to define and create the interference graph, attempt to color the graph, choose a spill candidate, and spill registers to the stack.
  * `src/scheduling`: Contains the code to do local instruction scheduling. This code will identify basic blocks, determine the data dependencies, calculate the heuristics, build the schedule, and rearrange the instructions. This also contains the functionality
  for trace scheduling including indentifying the trace, scheduling, and merging into the graph.
The main file that calls all the modules and defines the order is in `src/milestone.py`. This file also parses the arguments.
