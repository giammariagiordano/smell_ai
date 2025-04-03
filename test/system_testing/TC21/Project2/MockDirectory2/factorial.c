#include <stdio.h>

int main() {
    int numero, fattoriale = 1;

    printf("Inserisci un numero intero positivo: ");
    scanf("%d", &numero);

    if (numero < 0) {
        printf("Il fattoriale non è definito per numeri negativi.\n");
    } else {
        for (int i = 1; i <= numero; i++) {
            fattoriale *= i;
        }
        printf("Il fattoriale di %d è %d.\n", numero, fattoriale);
    }

    return 0;
}
