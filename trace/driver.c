
#include <stdio.h>
#include <stdlib.h>

int trace(int *X, int *Y, int *Z, int i);

int main() {
    srand(1234);
    int X[] = {rand() + 1, rand() + 1};
    int Y[] = {rand() + 1, rand() + 1};
    int Z[] = {rand() + 1, rand() + 1};
    unsigned i;
    unsigned j;

    for (i=0; i<10000; ++i) {
        printf("%d\n", trace(X, Y, Z, i%2));
        printf("%d\n", trace(Y, X, Z, i%2));
        printf("%d\n", trace(Z, X, Y, i%2));
        printf("\n");
        for (j=0; j<2; ++j) {
            printf("X[%u] = %d\n", j, X[j]);
            printf("Y[%u] = %d\n", j, Y[j]);
            printf("Z[%u] = %d\n", j, Z[j]);
        }
        printf("\n\n");
    }


}
