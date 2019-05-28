#include <stdlib.h>

void matadd(int **, int **, int **, unsigned int, unsigned int);

////////////////////////////////////////////////////////////////////////////////
//! C = A * B
//! @param C          result matrix
//! @param A          matrix A 
//! @param B          matrix B
//! @param hA         height of matrix A and B
//! @param wB         width of matrix A and B
////////////////////////////////////////////////////////////////////////////////

void matadd(int ** C, int ** A, int ** B, unsigned int height, 
    unsigned int width)
{
  for (unsigned int i = 0; i < height; ++i)
    for (unsigned int j = 0; j < width; ++j) {
      C[i][j] = A[i][j] + B[i][j];
    }
}

