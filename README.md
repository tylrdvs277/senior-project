# Milestone 4
## Tyler Davis (tylrdvs277)
### Build Instructions
* This requires some Python distribution to run (please use Python3 >=3.7)
* This implementation uses a Makefile to configure the environment and run on the provided input
* The Makefile has 5 targets: `all`, `assemble`, `build`, `test`, and `clean`
    * `all` (default/optional): runs `assemble`, `build`, and `test`
    * `assemble`: builds the .s files for matadd, regtest1, regtest2, and vecsort
    * `build`: builds the complete program executables by invoking `make(1)` in the subdirectories
    * `test`: run the executable and prints or runs `diff(1)` on the outputs except regtest
    * `clean`: removes object files by invoking `make clean` in the subdirectories
```
make [all|build|test|clean]
```
### Run Instructions
* If you want to run the program on another input file, the program can be invoked on its own
* Invoke the following command
```
python3 src/milestone4.py <input expand file> <output assembly file>
```
* The result will be that `<output assembly file>` contains the assembly language representation of the rtl
### Performance Results
Here are the performance results for running vecsort (a bubble sort of a length 65536 array)
```
Allocating and Initializing Vector V of size 65536:
Sorting Vector V:
Printing Vector:
******************************************************
Done.

 Performance counter stats for './vecsort':

      18827.790685      task-clock:u (msec)       #    0.998 CPUs utilized          
                 0      context-switches:u        #    0.000 K/sec                  
                 0      cpu-migrations:u          #    0.000 K/sec                  
               162      page-faults:u             #    0.009 K/sec                  
    22,497,762,030      cycles:u                  #    1.195 GHz                    
    20,447,458,598      instructions:u            #    0.91  insn per cycle         
     2,152,792,978      branches:u                #  114.341 M/sec                  
       663,020,672      branch-misses:u           #   30.80% of all branches        

      18.874762259 seconds time elapsed
```
