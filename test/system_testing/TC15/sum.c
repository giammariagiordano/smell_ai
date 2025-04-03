#include <stdio.h>

/**
 * Calcola la somma di due numeri interi.
 * 
 * @param a Primo numero intero.
 * @param b Secondo numero intero.
 * @return La somma dei due numeri.
 */
int somma(int a, int b) {
    return a + b;
}

int main() {
    int num1, num2, risultato;

    // Input dei numeri da parte dell'utente
    printf("Inserisci il primo numero: ");
    scanf("%d", &num1);

    printf("Inserisci il secondo numero: ");
    scanf("%d", &num2);

    // Calcolo della somma
    risultato = somma(num1, num2);

    // Stampa del risultato
    printf("La somma di %d e %d è: %d\n", num1, num2, risultato);

    return 0;
}
