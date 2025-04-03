import pandas as pd


def chain_indexing():
    # Creazione di un DataFrame di esempio
    data = {
        "A": [{"subkey1": 1, "subkey2": 2}, {"subkey1": 3, "subkey2": 4}],
        "B": [5, 6],
    }
    df = pd.DataFrame(data)

    # Chain indexing improprio
    value = df["A"][0]["subkey1"]  # Accesso concatenato (chain indexing)
    print(value)

    # Suggerimento: utilizzare il metodo at/loc/iat per evitare chain indexing
