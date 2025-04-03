import pandas as pd


def chain_index_example():
    # Creazione di un DataFrame di esempio
    df = pd.DataFrame([1, 2, 3, 4], [5, 6, 7, 8])

    col = 1
    x = 0

    # Accesso concatenato (chain indexing)
    df[col][x] = 9
    df.loc[x, col] = 9
