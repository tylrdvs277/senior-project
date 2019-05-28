Correct output is in vector.sorted.

GCC's perf stats below.

```
make -f Makefile.cpp clean

make -f Makefile.cpp

perf stat ./vecsort > vector.sorted
Allocating and Initializing Vector V of size 65536:
Sorting Vector V:
Printing Vector:
******************************************************
Done.

 Performance counter stats for './vecsort':

       23766.169813      task-clock:u (msec)       #    0.998 CPUs utilized          
                  0      context-switches:u        #    0.000 K/sec                  
                  0      cpu-migrations:u          #    0.000 K/sec                  
                160      page-faults:u             #    0.007 K/sec                  
     28,294,057,501      cycles:u                  #    1.191 GHz                    
     28,274,072,131      instructions:u            #    1.00  insn per cycle         
      4,298,632,316      branches:u                #  180.872 M/sec                  
        663,131,903      branch-misses:u           #   15.43% of all branches        
                                                                                      23.817480737 seconds time elapsed
```
