
/* Matrix addition: C = A + B. */

#define MSIZE 1024

// includes, system
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#ifndef _CPP_
extern "C"
#endif

void matadd(int**, int**, int**, unsigned int, unsigned int); 

void PrintMat(int**, unsigned int, unsigned int);

int** AllocateMatrix(unsigned int height, unsigned int width, int init);

////////////////////////////////////////////////////////////////////////////////
// Program main
////////////////////////////////////////////////////////////////////////////////
int main(int argc, char** argv) {

  // Matrices for the program
  int **M;
  int **N;
  int **P;
  unsigned int height = MSIZE;
  unsigned int width = MSIZE;
  //  Assuming square matrices, so the sizes of M, N and P are equal

  srand(2017);

  // Check command line for input matrix files
  if(argc == 1) 
  {
    // No inputs provided
    // Allocate and initialize the matrices
    fprintf(stderr,"Allocating and Initializing Matrix A:\n");
    M  = AllocateMatrix(height, width, 1);
    //PrintMat(M, height, width);
    fprintf(stderr,"Allocating and Initializing Matrix B:\n");
    N  = AllocateMatrix(height, width, 1);
    //PrintMat(N, height, width);
    fprintf(stderr,"Allocating and Initializing Matrix C:\n");
    P  = AllocateMatrix(height, width, 0);
  }
  else
  {
    printf("Usage: matmul > outfile\n");
    return 1;
  }
  
  fprintf(stderr,"Computing Iteration 1 of Matrix Sum:\n");
  matadd(P, M, N, height, width);
  for (int i=0; i<18; i+=2) {
    fprintf(stderr,"Computing Iteration %d of Matrix Sum:\n", i+2);
    matadd(P, M, P, height, width);
    fprintf(stderr,"Computing Iteration %d of Matrix Sum:\n", i+3);
    matadd(P, P, N, height, width);
  }
  fprintf(stderr,"Computing Iteration 20 of Matrix Sum:\n");
  matadd(P, P, P, height, width);

  PrintMat(P, height, width);

  // Free matrices
  for (unsigned int i = 0; i < height; i++) {
    free(M[i]);
    free(N[i]);
    free(P[i]);
  }
  free(M);
  free(N);
  free(P);

  return 0;
}

// Allocate a matrix of dimensions height*width
//	If init == 0, initialize to all zeroes.  
//	If init == 1, perform random initialization.
int** AllocateMatrix(unsigned int height, unsigned int width, int init)
{
  int **M;

  M = (int**) malloc(height*sizeof(int *));

  for(unsigned int i = 0; i < height; i++)
  {
    M[i] = (int*) malloc(width*sizeof(int));
    for (unsigned int j = 0; j < width; j++) 
    {
      M[i][j] = (init == 0) ? (0) : 
        ((1000*(rand()-(RAND_MAX/2))/(RAND_MAX/1000)));
    }
  }
  return M;
}	

// Write a matrix to file
void PrintMat(int **M, unsigned int height, unsigned int width)
{
  /*** Print results ***/
  fprintf(stderr,"Printing Result Matrix:\n");
  for (unsigned int i=0; i<height; i++)
  {
    for (unsigned int j=0; j<width; j++) 
      fprintf(stdout, "%d ", M[i][j]);
    fprintf(stdout, "\n"); 
  }
  fprintf(stderr,"******************************************************\n");
  fprintf(stderr,"Done.\n");
}
