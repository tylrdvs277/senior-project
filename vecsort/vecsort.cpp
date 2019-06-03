void vecsort(int*, unsigned int);

// A function to implement bubble sort 
void vecsort(int* vec, unsigned int length) 
{ 
  unsigned int i, j; 
  for (i = 0; i < length-1; i++)
  {
    // Last i elements are already in place    
    for (j = 0; j < length-i-1; j++)
    {
      if (vec[j] > vec[j+1]) 
      {
        int temp = vec[j];
        vec[j] = vec[j+1];
        vec[j+1] = temp;
      }
    }
  }
} 
