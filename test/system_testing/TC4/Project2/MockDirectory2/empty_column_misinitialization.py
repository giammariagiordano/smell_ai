import pandas as pd


def initialize_empty_column():
    df = pd.DataFrame()
    df["col1"] = ""  # Smell: inizializzazione con stringa vuota
    df["col2"] = 0  # Smell: inizializzazione con zero
    return df
