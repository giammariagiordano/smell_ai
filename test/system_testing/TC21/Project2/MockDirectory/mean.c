#include <stdio.h>

int main() {
    float num1, num2, num3, media;

    printf("Inserisci il primo numero: ");
    scanf("%f", &num1);
    printf("Inserisci il secondo numero: ");
    scanf("%f", &num2);
    printf("Inserisci il terzo numero: ");
    scanf("%f", &num3);

    media = (num1 + num2 + num3) / 3;
    printf("La media dei numeri %.2f, %.2f e %.2f è %.2f.\n", num1, num2, num3, media);

    return 0;
}
