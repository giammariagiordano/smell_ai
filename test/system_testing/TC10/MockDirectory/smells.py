import pandas as pd
import tensorflow as tf


def chain_index_example():
    # Creazione di un DataFrame di esempio
    df = pd.DataFrame([1, 2, 3, 4], [5, 6, 7, 8])

    col = 1
    x = 0

    # Accesso concatenato (chain indexing)
    df[col][x] = 9
    df.loc[x, col] = 9


def dataframe_conversion_api_misused():
    data = {"A": [1, 2, 3], "B": [4, 5, 6]}
    df = pd.DataFrame(data)

    # Uso scorretto di `.values`
    array = df.values  # Punto di rilevamento # noqa


def ts_array():
    for i in range(5):
        arr = tf.constant(  # noqa
            [i]
        )  # Punto di rilevamento: Uso scorretto di `tf.constant` in un ciclo
