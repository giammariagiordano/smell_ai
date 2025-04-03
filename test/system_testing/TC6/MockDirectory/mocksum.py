def sum_numbers(numbers):
    if not numbers:
        return 0

    total = 0
    for number in numbers:
        total += number

    return total


# Esempio di utilizzo
if __name__ == "__main__":
    numbers_list = [1, 2, 3, 4, 5]
    result = sum_numbers(numbers_list)
    print(f"La somma dei numeri è: {result}")
