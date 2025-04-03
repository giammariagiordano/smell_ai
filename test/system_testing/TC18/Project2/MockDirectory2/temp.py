def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


if __name__ == "__main__":
    temp_celsius = float(input("Inserisci la temperatura in gradi Celsius: "))
    temp_fahrenheit = celsius_to_fahrenheit(temp_celsius)
    print(f"{temp_celsius:.2f}°C corrispondono a {temp_fahrenheit:.2f}°F.")
