def check_even(number):
    if number % 2 == 0:
        return "Pari"
    else:
        return "Dispari"


# Esempio di utilizzo
if __name__ == "__main__":
    num = 10
    result = check_even(num)
    print(f"Il numero {num} è {result}.")
