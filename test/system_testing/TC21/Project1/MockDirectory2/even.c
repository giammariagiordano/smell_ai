#include <stdio.h>

int main() {
    int numero;

    printf("Inserisci un numero: ");
    scanf("%d", &numero);

    if (numero % 2 == 0) {
        printf("Il numero %d è pari.\n", numero);
    } else {
        printf("Il numero %d è dispari.\n", numero);
    }

    return 0;
}
