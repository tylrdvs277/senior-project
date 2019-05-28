
/* Vector Sort */

#define VSIZE 4194304

// includes, system
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#ifndef _CPP_
extern "C"
#endif

void vecsort(int*, unsigned int); 

void PrintVec(int*, unsigned int);

int* AllocateVector(unsigned int length, int init);

void swap(int*, int*);

//////////////////////////////////////////////////////////////////////////////
// Program main
//////////////////////////////////////////////////////////////////////////////
int main(int argc, char** argv) {

  // Vector for the program
  int *V;
  unsigned int length = VSIZE>>6;

  srand(2019);

  // Check command line 
  if(argc == 1) 
  {
    // No inputs provided
    // Allocate and initialize the matrices
    fprintf(stderr,"Allocating and Initializing Vector V of size %u:\n", 
        length);
    V  = AllocateVector(length, 1);
  }
  else
  {
    printf("Usage: vecsort > outfile\n");
    return 1;
  }
  
  fprintf(stderr,"Sorting Vector V:\n");
  vecsort(V, length);

  PrintVec(V, length);

  // Free vector
  free(V);

  return 0;
}

// Allocate a vector of length length
//	If init == 0, initialize to all zeroes.  
//	If init == 1, perform random initialization.
int* AllocateVector(unsigned int length, int init)
{
  int *V;

  V = (int*) malloc(length*sizeof(int));

  for(unsigned int i = 0; i < length; i++)
  {
    V[i] = (init == 0) ? (0) : 
      ((100000*(rand()-(RAND_MAX/2))/(RAND_MAX/100000)));
  }
  return V;
}	

// Write a vector to file
void PrintVec(int *V, unsigned int length)
{
  /*** Print results ***/
  fprintf(stderr,"Printing Vector:\n");
  for (unsigned int i=0; i<length; i++)
  {
    fprintf(stdout, "%d ", V[i]);
  }
  fprintf(stderr,"******************************************************\n");
  fprintf(stderr,"Done.\n");
}

void swap(int *xp, int *yp) 
{ 
  int temp = *xp; 
  *xp = *yp; 
  *yp = temp; 
} 

