def calcola_media(numeri):

    if not numeri:
        return None
    return sum(numeri) / len(numeri)


if __name__ == "__main__":
    lista_numeri = [10, 20, 30, 40, 50]
    media = calcola_media(lista_numeri)

    if media is not None:
        print(f"La media dei numeri è: {media:.2f}")
    else:
        print("La lista è vuota, impossibile calcolare la media.")
