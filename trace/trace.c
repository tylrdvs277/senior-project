
int trace(int *X, int *Y, int *Z, int i) {
    int b = Y[i];
    int a;
    if (b != 0) {
        a = Z[0];
        Y[i] = a;
    } else {
        b = X[i];
    }
    Z[i] = b + X[i];

    return b;
}
